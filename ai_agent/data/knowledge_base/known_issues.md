# TreeLine Known Issues

Below is a list of current known issues affecting the TreeLine platform. Our engineering team is actively working on solutions. Where applicable, temporary workarounds are provided.

_Last updated: July 20, 2025_

---

## 🔒 Login Loop on Firefox (v2.4.1)

**Issue:**  
Some users are stuck in a login loop when using Firefox after enabling 2FA.

**Workaround:**  
Clear browser cookies or switch to Chrome/Edge temporarily.

**Status:**  
Fix deployed in internal beta – will be included in v2.4.2.

---

## 📁 Upload Fails for Files Over 100MB

**Issue:**  
File uploads larger than 100MB may time out or return a silent error.

**Workaround:**  
Split the file or compress it before uploading.

**Status:**  
Fix scheduled for August 2025 release.

---

## 📆 Calendar Events Not Syncing with Outlook

**Issue:**  
Some events created in TreeLine are not appearing in linked Outlook calendars.

**Workaround:**  
Re-authenticate your Outlook integration under Settings > Integrations.

**Status:**  
Under investigation.

---

## 🔔 Duplicate Notifications for Team Mentions

**Issue:**  
Users may receive multiple notifications for the same team mention in discussions.

**Workaround:**  
None currently – this is purely a display issue and does not affect functionality.

**Status:**  
Bug fix expected in next minor patch.

---

## 📊 Inaccurate Task Progress in Analytics Report

**Issue:**  
The progress percentage in project analytics sometimes shows outdated values.

**Workaround:**  
Refresh the report or re-generate it to force data sync.

**Status:**  
Fix in testing phase.

---

We appreciate your patience as we work to resolve these issues.  
For updates, visit our [status page](https://status.treeline.com) or contact [support@treeline.com](mailto:support@treeline.com).
