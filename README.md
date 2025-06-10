1. RAW_JSON='...'
You're defining a multi-line JSON object with key-value pairs (like product name, owner, tags, etc.).

2. ENCODED_JSON=$(echo "$RAW_JSON" | base64 -w0)
You're encoding the JSON into a base64 string (so it becomes a safe single-line value for GitHub to handle in outputs/env).

3. echo "... >> $GITHUB_ENV"
This makes the encoded string available as an environment variable for later steps in the same job (in case you want to echo $DEPLOY_META_JSON within deploy).

4. echo "... >> $GITHUB_OUTPUT"
This is the key part — it declares DEPLOY_META_JSON as a named output of the job (from the set-meta step).

After that 
notify:
  needs: deploy
  uses: ./.github/workflows/gmailNotification.yaml
  with:
    DEPLOY_META_JSON: ${{ needs.deploy.outputs.DEPLOY_META_JSON }}

Passing the exact same base64-encoded version of the original RAW_JSON into the gmailNotification.yaml workflow.
And then inside that workflow, you do:
  echo "$DEPLOY_META_JSON" | base64 -d | jq ...
     Decode the base64 string back into the original JSON and loop through it.



    RAW_JSON:  	 Your actual metadata in JSON
    
   ENCODED_JSON:  	Base64-encoded version of RAW_JSON
   
   GITHUB_OUTPUT:  	Makes ENCODED_JSON available to next job
   
   needs.deploy.outputs.DEPLOY_META_JSON:	Passes that encoded string to the next job
   
  base64 -d : in Gmail job	Recovers the original metadata safely for email















  # Teams + Email Notification Workflow

This README explains the `teams-notification-source.yml` workflow line by line, describing the purpose and usage of each section. Use this as a reference when you need to customize or troubleshoot the workflow.

---

## Table of Contents

1. [Workflow Metadata](#workflow-metadata)
2. [Inputs & Secrets](#inputs--secrets)
3. [Jobs](#jobs)

   * [notify-and-email Job](#notify-and-email-job)

     * [Checkout Repository](#1-checkout-repository)
     * [Capture Timestamps](#2-capture-timestamps)
     * [Setup Python](#3-setup-python)
     * [Run Python Script](#4-run-python-script)
4. [Python Script Overview](#python-script-overview)

   * [Decoding Payload](#decoding-payload)
   * [Environment Variables & Context](#environment-variables--context)
   * [Building Teams Message](#building-teams-message)
   * [Sending to Teams](#sending-to-teams)
   * [Building HTML Email](#building-html-email)
   * [Sending Email](#sending-email)

---

## Workflow Metadata

```yaml
name: Teams + Email Notification Workflow
```

* **Purpose**: Sets the display name of the workflow in GitHub Actions.

```yaml
on:
  workflow_call:
```

* **Purpose**: Declares this as a reusable workflow that can be invoked by other workflows via `workflow_call`.

---

## Inputs & Secrets

```yaml
inputs:
  DEPLOY_META_JSON:
    description: 'Base64-encoded JSON with deployment metadata (must include branch, version, product, env, status)'
    required: true
    type: string
```

* **DEPLOY\_META\_JSON**: Encoded JSON payload containing keys: `branch`, `version`, `product`, `env`, `status`.

```yaml
secrets:
  TEAMS_WEBHOOK_URL:
    description: 'Teams Incoming Webhook URL'
    required: true
```

* **TEAMS\_WEBHOOK\_URL**: Incoming webhook URL for Microsoft Teams. Stored securely in GitHub secrets.

---

## Jobs

### notify-and-email Job

```yaml
jobs:
  notify-and-email:
    runs-on: arc-rs-nonprod   # or ubuntu-latest
```

* **runs-on**: Specifies the runner label. Use your self-hosted runner (`arc-rs-nonprod`) or `ubuntu-latest`.

#### 1. Checkout Repository

```yaml
- name: Checkout repo
  uses: actions/checkout@v4
```

* **Purpose**: Clones the repository so that `mail.py` and other code are available.

#### 2. Capture Timestamps

```yaml
- name: Capture timestamps
  run: |
    echo "BUILD_START=$(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> $GITHUB_ENV
    echo "BUILD_END=$(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> $GITHUB_ENV
```

* **BUILD\_START** / **BUILD\_END**: Record start and end times in UTC. Written to environment for later use.

#### 3. Setup Python

```yaml
- name: Generate & send notifications with Python
  uses: actions/setup-python@v4
```

* **Purpose**: Installs and prepares Python for the subsequent script execution.

#### 4. Run Python Script

```yaml
- name: Run Python to build & send
  env:
    INPUT_DEPLOY_META_JSON: ${{ inputs.DEPLOY_META_JSON }}
    BUILD_START:              ${{ env.BUILD_START }}
    BUILD_END:                ${{ env.BUILD_END }}
    GITHUB_SHA:               ${{ github.sha }}
    GITHUB_RUN_NUMBER:        ${{ github.run_number }}
    GITHUB_REPOSITORY:        ${{ github.repository }}
    GITHUB_ACTOR:             ${{ github.actor }}
    TEAMS_WEBHOOK_URL:        ${{ secrets.TEAMS_WEBHOOK_URL }}
    EMAIL_TO:                 yourname@yourcompany.com
  run: |
    python3 << 'EOF'
    ...
    EOF
```

* **Environment variables**: Passes all required context and secrets into the Python snippet.
* **EMAIL\_TO**: Replace `yourname@yourcompany.com` with your actual email or use a secret.

---

## Python Script Overview

The embedded Python snippet handles:

### Decoding Payload

```python
payload = json.loads(base64.b64decode(os.environ['INPUT_DEPLOY_META_JSON']))
```

* **Purpose**: Converts the base64-encoded JSON string into a Python dict.

### Environment Variables & Context

```python
branch  = payload['branch']
version = payload['version']
product = payload['product']
envname = payload['env']
status  = payload['status'].upper()
```

* **Requirements**: Fails if any key is missing, ensuring all required metadata is supplied.

Additional context variables are read from `os.environ` for build times, commit info, and GitHub context.

### Building Teams Message

A Python dict `teams_msg` is created with the MessageCard schema, including:

* `themeColor`, `summary`
* Two sections: Build Information & Release Information
* `potentialAction` links to the workflow run and commit history

### Sending to Teams

```python
resp = requests.post(
  os.environ['TEAMS_WEBHOOK_URL'],
  json=teams_msg,
  headers={'Content-Type':'application/json'}
)
resp.raise_for_status()
```

* **Purpose**: Posts the JSON payload to Teams using the `requests` library.

### Building HTML Email

```python
rows = ""
for section in teams_msg['sections']:
  for fact in section['facts']:
    rows += f"<tr><td><b>{fact['name']}</b></td><td>{fact['value']}</td></tr>\n"
html = f"""
<html>
  <body>
    <h2>Build & Release Notification</h2>
    <table border="1" cellpadding="6" cellspacing="0">
      {rows}
    </table>
    ...
"""
```

* **Purpose**: Reuses the same facts to generate an HTML table for the email body.

### Sending Email

```python
subprocess.check_call([
  "python3", ".github/workflows/mail.py",
  to_addr, subject, "email_body.html"
])
```

* **Purpose**: Invokes your existing `mail.py` script to send the HTML email via SMTP.

---

**Usage:**

1. **Invoke** this workflow from another workflow using `uses:` and pass `DEPLOY_META_JSON`.
2. **Ensure** you have defined `TEAMS_WEBHOOK_URL` and `COMPANY_EMAIL` (or `EMAIL_TO`) in secrets.
3. **Customize** any fields (e.g., additional facts) by extending the Python snippet.

Feel free to reach out if you need further customization or integration details!

