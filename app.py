#!/usr/bin/env python3

import base64
import json
import os
import time
import hmac
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = int(os.environ["LISTEN_PORT"])

NEXTCLOUD_URL = os.environ["NEXTCLOUD_URL"].rstrip("/")
NEXTCLOUD_USER = os.environ["NEXTCLOUD_USER"]
NEXTCLOUD_APP_PASSWORD = os.environ["NEXTCLOUD_APP_PASSWORD"]
NEXTCLOUD_TLS_VERIFY = os.environ["NEXTCLOUD_TLS_VERIFY"].lower() in ("1", "true", "yes")
TALK_TOKEN = os.environ["TALK_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]


# TLS certificate verification for the InfluxDB connection
if NEXTCLOUD_TLS_VERIFY:
    SSL_CONTEXT = ssl.create_default_context()
else:
    # Disable TLS verification for InfluxDB certificate
    SSL_CONTEXT = ssl._create_unverified_context()


def send_to_talk(message):
    url = (
        f"{NEXTCLOUD_URL}"
        f"/ocs/v2.php/apps/spreed/api/v1/chat/{TALK_TOKEN}"
    )

    payload = json.dumps({
        "message": message
    }).encode("utf-8")

    credentials = (
        f"{NEXTCLOUD_USER}:{NEXTCLOUD_APP_PASSWORD}"
    ).encode("utf-8")

    auth = base64.b64encode(credentials).decode("ascii")

    request = Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "OCS-APIRequest": "true",
        },
    )

    with urlopen(
        request,
        timeout=15,
        context=SSL_CONTEXT
    ) as response:

        body = response.read().decode(
            "utf-8",
            errors="replace"
        )

        print(
            f"Nextcloud: HTTP {response.status}: {body}",
            flush=True
        )

        if response.status not in (200, 201):
            raise RuntimeError(
                f"Nextcloud returned HTTP {response.status}"
            )


def severity_icon(severity):
    icons = {
        "error": "🚨",
        "warning": "⚠️",
        "notice": "ℹ️",
        "info": "ℹ️",
        "unknown": "❓",
    }

    return icons.get(
        str(severity).lower(),
        "🔔"
    )


def format_message(data):

    title = str(
        data.get(
            "title",
            "Proxmox notification"
        )
    )

    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()

    severity = str(
        data.get(
            "severity",
            "unknown"
        )
    )

    timestamp = data.get("timestamp")
    fields = data.get("fields") or {}

    hostname = fields.get("hostname")
    node = fields.get("node")
    vmid = fields.get("vmid")
    job_id = fields.get("job-id")
    event_type = fields.get("type")

    lines = []

    lines.append(
        f"{severity_icon(severity)} **{title}**"
    )

    lines.append("")

    lines.append(
        f"**Severity:** `{severity}`"
    )

    if hostname:
        lines.append(
            f"**Host:** `{hostname}`"
        )

    if node:
        lines.append(
            f"**Node:** `{node}`"
        )

    if vmid:
        lines.append(
            f"**VMID:** `{vmid}`"
        )

    if job_id:
        lines.append(
            f"**Job:** `{job_id}`"
        )

    if event_type:
        lines.append(
            f"**Event:** `{event_type}`"
        )

    if timestamp:
        try:
            formatted = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(int(timestamp))
            )

            lines.append(
                f"**Time:** `{formatted}`"
            )

        except Exception:
            pass

# cut message after 600 characters. Backup notifications can be quiet long
    if message:
        lines.append("")
        lines.append("```text")
        lines.append(message[:600])
        lines.append("```")

    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(
            f"{self.client_address[0]} - "
            f"{fmt % args}",
            flush=True
        )

    def send_json(self, status, data):

        payload = json.dumps(
            data
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(payload))
        )

        self.end_headers()

        self.wfile.write(payload)

    def do_GET(self):

        if self.path == "/health":

            self.send_json(
                200,
                {
                    "status": "ok"
                }
            )

            return

        self.send_json(
            404,
            {
                "error": "not found"
            }
        )

    def do_POST(self):

        if self.path != "/proxmox":

            self.send_json(
                404,
                {
                    "error": "not found"
                }
            )

            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

        except ValueError:
            length = 0

        if length <= 0 or length > 1024 * 1024:

            self.send_json(
                400,
                {
                    "error": "invalid content length"
                }
            )

            return

        body = self.rfile.read(length)

        supplied_secret = self.headers.get(
            "X-Proxmox-Webhook-Secret",
            ""
        )

        if not hmac.compare_digest(
            supplied_secret,
            WEBHOOK_SECRET
        ):

            print(
                "Rejected webhook: invalid secret",
                flush=True
            )

            self.send_json(
                401,
                {
                    "error": "unauthorized"
                }
            )

            return

        try:

            data = json.loads(
                body.decode("utf-8")
            )

        except Exception as e:

            print(
                f"Invalid JSON: {e}",
                flush=True
            )

            self.send_json(
                400,
                {
                    "error": "invalid json"
                }
            )

            return

        print(
            "Received Proxmox notification:",
            json.dumps(
                data,
                indent=2
            ),
            flush=True
        )

        try:

            message = format_message(
                data
            )

            send_to_talk(
                message
            )

            self.send_json(
                200,
                {
                    "status": "sent"
                }
            )

        except Exception as e:

            print(
                f"Failed to send Talk message: {e}",
                flush=True
            )

            self.send_json(
                502,
                {
                    "error":
                    "failed to send to Nextcloud Talk"
                }
            )


if __name__ == "__main__":

    print(
        "Proxmox → Nextcloud Talk bridge "
        f"listening on {LISTEN_HOST}:{LISTEN_PORT}",
        flush=True
    )

    server = ThreadingHTTPServer(
        (LISTEN_HOST, LISTEN_PORT),
        Handler
    )

    server.serve_forever()
