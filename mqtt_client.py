# ============================================================
# mqtt_client.py — Publish panggilan meja ke ESP01 via MQTT
# Butuh: pip install paho-mqtt
# ============================================================

import paho.mqtt.publish as publish
from config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS, MQTT_TOPIC_PREFIX


def panggil_meja(nomor_meja: str) -> dict:
    """
    Publish pesan ke topic kasir/pager/{nomor_meja}
    ESP01 subscribe topic ini, lalu nyalakan buzzer + LED.

    Payload JSON: {"meja": "5", "aksi": "panggil"}
    """
    import json

    topic   = f"{MQTT_TOPIC_PREFIX}/{nomor_meja}"
    payload = json.dumps({"meja": str(nomor_meja), "aksi": "panggil"})

    auth = None
    if MQTT_USER:
        auth = {'username': MQTT_USER, 'password': MQTT_PASS}

    try:
        publish.single(
            topic,
            payload=payload,
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            auth=auth,
            qos=1
        )
        return {'success': True, 'topic': topic, 'payload': payload}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def reset_meja(nomor_meja: str) -> dict:
    """
    Publish reset ke ESP01 — matikan buzzer + LED.
    Payload JSON: {"meja": "5", "aksi": "reset"}
    """
    import json

    topic   = f"{MQTT_TOPIC_PREFIX}/{nomor_meja}"
    payload = json.dumps({"meja": str(nomor_meja), "aksi": "reset"})

    auth = None
    if MQTT_USER:
        auth = {'username': MQTT_USER, 'password': MQTT_PASS}

    try:
        publish.single(
            topic,
            payload=payload,
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            auth=auth,
            qos=1
        )
        return {'success': True}

    except Exception as e:
        return {'success': False, 'error': str(e)}