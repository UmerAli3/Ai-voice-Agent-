# Vapi Webhook Testing Examples & Code Snippets

This document contains practical HTTP request examples, script snippets, and cURL commands to test and send Vapi webhook payloads to `POST /webhook/vapi`.

---

## 1. cURL Command Example

```bash
curl -X POST "http://localhost:3000/webhook/vapi" \
  -H "Content-Type: application/json" \
  -H "x-vapi-secret: whsec_prod_9874563210_health_voice" \
  -d '{
    "message": {
      "type": "end-of-call-report",
      "call": {
        "id": "conv_vapi_99812_health",
        "status": "ended",
        "customer": {
          "number": "+15550198822",
          "name": "Eleanor Vance"
        },
        "artifact": {
          "transcript": "Agent: Hello Eleanor. Patient: Confirming my 10 AM appointment tomorrow with Dr. Harrison."
        },
        "analysis": {
          "summary": "Patient confirmed 10 AM cardiology appointment and received lab prep instructions.",
          "structuredData": {
            "patient_name": "Eleanor Vance",
            "dob": "1982-04-15",
            "reason": "Cardiology Appointment Confirmation"
          }
        }
      }
    }
  }'
```

---

## 2. Python (`httpx` / `requests`) Integration Example

```python
import json
import requests

WEBHOOK_URL = "http://localhost:3000/webhook/vapi"
SECRET_HEADER = "whsec_prod_9874563210_health_voice"

payload = {
    "message": {
        "type": "end-of-call-report",
        "call": {
            "id": "conv_py_test_10023",
            "customer": {
                "number": "+15550143322",
                "name": "Marcus Aurelius"
            },
            "analysis": {
                "summary": "Patient requested prescription refill for Lisinopril 10mg.",
                "structuredData": {
                    "patient_name": "Marcus Aurelius",
                    "dob": "1975-11-20",
                    "reason": "Prescription Refill Request"
                }
            },
            "artifact": {
                "transcript": "Agent: How can I help you? Patient: I need a refill for my blood pressure medication."
            }
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "x-vapi-secret": SECRET_HEADER
}

response = requests.post(WEBHOOK_URL, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {json.dumps(response.json(), indent=2)}")
```

---

## 3. Node.js JavaScript (`fetch`) Example

```javascript
const WEBHOOK_URL = 'http://localhost:3000/webhook/vapi';
const VAPI_SECRET = 'whsec_prod_9874563210_health_voice';

const samplePayload = {
  message: {
    type: 'end-of-call-report',
    call: {
      id: 'conv_node_call_7761',
      customer: {
        number: '+15550187766',
        name: 'Sophia Martinez'
      },
      analysis: {
        summary: 'Patient scheduled follow-up consultation for blood pressure check.',
        structuredData: {
          patient_name: 'Sophia Martinez',
          dob: '1990-08-12',
          reason: 'Hypertension Follow-up Appointment'
        }
      }
    }
  }
};

async function sendVapiWebhook() {
  const response = await fetch(WEBHOOK_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-vapi-secret': VAPI_SECRET
    },
    body: JSON.stringify(samplePayload)
  });

  const data = await response.json();
  console.log('HTTP Status:', response.status);
  console.log('Response JSON:', data);
}

sendVapiWebhook();
```

---

## 4. Expected Success HTTP Response (200 OK)

```json
{
  "status": "success",
  "message": "Vapi webhook payload parsed, verified, and stored successfully",
  "conversation_id": "conv_vapi_99812_health",
  "extracted_data": {
    "conversation_id": "conv_vapi_99812_health",
    "patient_name": "Eleanor Vance",
    "dob": "1982-04-15",
    "phone": "+15550198822",
    "reason": "Cardiology Appointment Confirmation",
    "summary": "Patient confirmed 10 AM cardiology appointment and received lab prep instructions.",
    "transcript": "Agent: Hello Eleanor. Patient: Confirming my 10 AM appointment tomorrow with Dr. Harrison."
  }
}
```

---

## 5. Expected Error HTTP Response (401 Unauthorized)

```json
{
  "error": {
    "code": "UNAUTHORIZED_WEBHOOK",
    "message": "Invalid or missing x-vapi-secret / signature header"
  }
}
```
