# Vapi Voice AI Platform Configuration & Integration Guide

This guide details the complete configuration instructions for connecting your Vapi Voice Agent platform with this FastAPI Healthcare backend webhook endpoint (`POST /webhook/vapi`).

---

## 1. Webhook Endpoint Configuration

### Server URL
In your Vapi Dashboard ([dashboard.vapi.ai](https://dashboard.vapi.ai/)) or Assistant JSON payload, configure the Server URL:

- **Primary Webhook Endpoint**: `https://<your-domain>/webhook/vapi`
- **Alternative Endpoint**: `https://<your-domain>/api/v1/webhook/vapi`

### HTTP Method & Headers
- **HTTP Method**: `POST`
- **Content-Type**: `application/json`
- **Secret Header**: `x-vapi-secret: <your_configured_vapi_webhook_secret>`

---

## 2. Server Secret & Authentication Setup

To secure webhook requests from unauthorized third parties:

1. In your `.env` file, set:
   ```env
   VAPI_WEBHOOK_SECRET=whsec_prod_9874563210_health_voice
   ```
2. In the Vapi Dashboard under **Account Settings** -> **Server Secret** (or Assistant Server settings), enter the exact matching secret value.
3. Every incoming HTTP POST request will validate `x-vapi-secret` or `x-vapi-signature` against `VAPI_WEBHOOK_SECRET`.

---

## 3. Configuring Assistant Structured Data Extraction in Vapi

In your Vapi Assistant configuration, enable structured output extraction so Vapi populates key patient information automatically at the end of the call:

```json
{
  "name": "Healthcare Intake Voice Assistant",
  "serverUrl": "https://api.yourdomain.com/webhook/vapi",
  "serverUrlSecret": "whsec_prod_9874563210_health_voice",
  "model": {
    "provider": "openai",
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": "You are a professional medical assistant intake agent. Ask the caller for their full name, date of birth (YYYY-MM-DD), phone number, and primary reason for calling. At the end of the call, summarize the conversation clearly."
      }
    ]
  },
  "structuredDataSchema": {
    "type": "object",
    "properties": {
      "patient_name": {
        "type": "string",
        "description": "Full legal name of the patient"
      },
      "dob": {
        "type": "string",
        "description": "Date of birth in YYYY-MM-DD format"
      },
      "reason": {
        "type": "string",
        "description": "Chief complaint or reason for healthcare consultation"
      }
    },
    "required": ["patient_name", "reason"]
  },
  "endOfCallReportServerUrl": "https://api.yourdomain.com/webhook/vapi"
}
```

---

## 4. Subscribed Webhook Events

Ensure your Vapi Assistant or Org configuration subscribes to:
- `end-of-call-report` *(Primary event triggering data extraction & database persistence)*
- `transcript` *(Optional live transcript stream)*

---

## 5. Summary of Extracted Database Fields

When a webhook POST payload hits `POST /webhook/vapi`, the backend automatically extracts and stores:

| Field Name | Description | Source in Vapi Payload |
| :--- | :--- | :--- |
| **Conversation ID** | Unique Call/Conversation UUID | `message.call.id` |
| **Patient Name** | Full name of patient | `message.call.analysis.structuredData.patient_name` or `message.call.customer.name` |
| **DOB** | Patient Date of Birth | `message.call.analysis.structuredData.dob` |
| **Phone** | Caller phone number | `message.call.customer.number` |
| **Reason** | Appointment or inquiry reason | `message.call.analysis.structuredData.reason` |
| **Summary** | AI generated call summary | `message.call.analysis.summary` or `message.call.artifact.transcript` |
