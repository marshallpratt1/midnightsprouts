# Midnight Sprouts

Django dashboard and Raspberry Pi greenhouse controller. The control worker is
`scripts/hardware.py`; run it using `python manage.py runscript hardware`.
Python 3.9+ is required (the controller uses the standard-library `zoneinfo`).

## Output modes and watering

Every output has an independent persistent AUTO/MANUAL mode on the dashboard.
The group buttons set all eight modes at once. Mixed mode is displayed explicitly.
Entering MANUAL preserves the current output; use its ON/OFF or OPEN/CLOSED
button to change it. Returning to AUTO applies its control logic on the next
hardware cycle. Mode changes and manual commands require a superuser on the server.
Migration initializes individual modes from the existing system-wide mode.

Pump/valve schedules advance even in MANUAL, anchored to the configured local
start time and repeat interval in America/Anchorage. Manual output changes never
move that anchor. Expired windows are skipped, not replayed. Returning to AUTO
inside a window runs only its remaining duration; outside a window, the output
turns off and waits. The same rules handle controller downtime. Overnight windows
are supported. Schedules use a frequency of 1–365 days; duration 0 disables them,
and existing zero-frequency schedules remain disabled until configured.
Duration is limited to 1440 minutes. Saving an edited schedule intentionally
sets its new anchor to the next occurrence of the selected start time.

Local start times follow daylight saving time. A nonexistent spring 02:xx start
moves to 03:xx for that day; a repeated autumn hour runs once at its first
occurrence. Durations measure elapsed minutes. Manual mode continues to bypass
automatic scheduling and the pump temperature interlock, as it did previously.
An AUTO pump turns off or stays off if water is at/below 32°F or its sensor is stale.

## Sensor failures and email alerts

A sensor is stale at 60 seconds without a valid scan. Failed CRCs, missing values,
non-finite numbers, and readings outside sensor physical ranges do not count as
valid scans. Each probe is read independently so one failed probe does not skip
others. DHT retries are bounded to one attempt per cycle.

For both nursery and water heaters **in AUTO**, stale temperature means:

- Before May 15, using Anchorage's date: heater ON.
- May 15 and later: heater OFF.
- On recovery: normal setpoint/hysteresis logic resumes.
- In MANUAL: preserve the manual command regardless of sensor failure.

This seasonal rule assumes the user operates the system March–October; it does
not automatically start or shut down the greenhouse. The pre-May fallback can
hold a heater ON indefinitely; each heater's independent thermostat/temperature
cutoff remains important. The vent uses any valid high-temperature/high-humidity
opening request; it retains its prior state when it cannot establish normal
closing conditions from valid readings.

After ten minutes without a valid scan, queue one fault email for each affected
sensor (greenhouse temperature, nursery temperature, water temperature, humidity).
Queue one recovery message when readings resume. Include last reading/time and
fallback information in the fault email. Alerts are sent even in MANUAL.
Health and queued alerts survive restarts. At first initialization, existing
sensor readings provide the last-valid timestamp; a sensor with no history starts
its alert timer when monitoring begins. Consequently, startup after a long
shutdown may report the old outage and its recovery.

A **separate mail process** delivers notifications to `your-account@yahoo.com`.
SMTP is never called from the control loop. Failed delivery is retried with
backoff (up to one hour), preserving fault-before-recovery order. A local lock
prevents overlapping mail workers. Delivery is at-least-once: a crash after SMTP
acceptance but before saving the result can cause a duplicate email. The minute
mail schedule means fault emails normally arrive on the next minute after the
10-minute threshold, subject to network/provider delays.

These alerts require the hardware worker, mail worker, and internet to work.
They cannot report a powered-off Pi or a stopped hardware process. Email itself
is not an independent safety mechanism.

### Configure the sending account on the Pi

Use the existing private environment configuration (Django reads `greenhouse/.env`
by default) or service environment variables. Do not commit credentials. The
recipient can be Yahoo even when the sending provider is different.

```dotenv
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-account@yahoo.com
EMAIL_HOST_PASSWORD=your-yahoo-app-password
DEFAULT_FROM_EMAIL=your-account@yahoo.com
GREENHOUSE_ALERT_RECIPIENT=your-account@yahoo.com
```

Generate a dedicated app password in [Yahoo Account Security](https://login.yahoo.com/account/security)
for this greenhouse application and enter it directly in the Pi's private
configuration. Use the generated app password, not the regular account password.
These settings use Yahoo SMTP with implicit TLS on port 465; see
[Yahoo's server settings](https://help.yahoo.com/kb/SLN4075.html).
The SMTP socket timeout is 15 seconds. Confirm delivery after configuration:

```bash
python manage.py send_sensor_alerts --test
```

No real email is sent by the automated tests.

## Three-month retention

Preview first, then apply:

```bash
python manage.py prune_history
python manage.py prune_history --apply
```

The cutoff is three **calendar months** ago in Anchorage, clamping month-end
dates when necessary. Deletes are batched at 1,000 rows to avoid one large
transaction blocking control writes. Temperature/humidity/water-level history,
old setpoints, output history, system-mode history, errors, and sent notifications
are pruned. **The newest row in every sensor/state/setpoint history table is
always retained**, even if older than three months: existing code depends on
these records. Last-frost data, users, individual modes, sensor health, and
unsent notifications are never pruned. Logging cadence remains unchanged.
SQLite can reuse freed pages; deleting rows does not necessarily shrink the file
on disk. No automatic VACUUM is run while controlling equipment.

Run the mail command every minute and retention daily as the same Unix user as
the application. Example user crontab (replace paths with the actual checkout
and virtual environment; preserve all other existing crontab entries):

```cron
* * * * * cd /home/pi/midnightsprouts && /home/pi/midnightsprouts/greenhouseenv/bin/python manage.py send_sensor_alerts
17 3 * * * cd /home/pi/midnightsprouts && /home/pi/midnightsprouts/greenhouseenv/bin/python manage.py prune_history --apply
```

The daily cron time follows the Pi's system timezone; retention always computes
its cutoff in Anchorage. Email/cleanup commands are inactive until scheduled.

## Deployment checklist

1. Confirm Python is at least 3.9 and identify the services launching Gunicorn
   and the hardware worker. Service names/paths are not stored in this repository.
2. Stop the hardware worker and web service for the migration. Record the current
   physical output states; process shutdown does not guarantee relays switch off.
3. Back up `db.sqlite3` while the application is stopped, and keep the prior code
   revision for rollback. Also preserve the private environment configuration.
4. Check out the reviewed branch/merged change and install the project's existing
   dependencies in its virtual environment. Do not run `scripts/seeddata.py` on
   an existing deployment: it writes new settings and fake readings.
5. Run `python manage.py migrate`, `python manage.py check`, and
   `python manage.py collectstatic --noinput`.
6. Configure SMTP, run the email setup test, preview history cleanup, and add the
   cron entries after confirming the paths and deletion counts.
7. Restart web and hardware services. Verify individual modes, relay operation,
   and the actual watering schedules. For summer nursery shutdown, select its
   heater's MANUAL mode and explicitly turn it OFF.
8. Verify the stale-temperature and recovery behavior with equipment supervised.
   Automated tests use fake GPIO; actual relay polarity and hardware operation
   still require a Pi check.

Rollback: stop both services, restore the matching code revision and database
backup, then restart. Retention permanently removes old history when deployed;
a backup is necessary to recover deleted readings.

## Development tests

Tests need Django, django-environ, django-extensions, and timezone data; they do
not import Pi libraries until the real hardware worker is started.

```bash
SECRET_KEY=development-test-key DEBUG=False python manage.py test
SECRET_KEY=development-test-key DEBUG=False python manage.py makemigrations --check --dry-run
```

Coverage includes mixed modes and authorization, mode migration, manual watering
without schedule shifts, expired/overnight windows and DST, stale/sensor-failure
boundaries and recovery, durable email retries, and retention exclusions.
