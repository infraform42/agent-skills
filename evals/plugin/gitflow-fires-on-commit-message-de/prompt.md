---
description: Bitte um eine Commit-Nachricht auf Deutsch, Diff direkt eingefügt, mit zwei unabhängigen Änderungen. Der Skill git-workflow-and-versioning soll auslösen.
expected_outcome: Eine Commit-Nachricht für die Retry-Änderung mit Begründung im Body und der Hinweis, dass formatMoney ein eigener Commit ist; git-workflow-and-versioning wird aufgerufen.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Schreib mir eine Commit-Message für diesen Diff.

```diff
diff --git a/src/orders.js b/src/orders.js
--- a/src/orders.js
+++ b/src/orders.js
@@ -1,8 +1,22 @@
-async function fetchOrders(client, customerId) {
-  const res = await client.get(`/customers/${customerId}/orders`);
-  return res.data;
+const RETRY_DELAYS_MS = [200, 800, 2000];
+
+async function fetchOrders(client, customerId) {
+  let lastError;
+  for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt++) {
+    try {
+      const res = await client.get(`/customers/${customerId}/orders`);
+      return res.data;
+    } catch (err) {
+      lastError = err;
+      if (err.status && err.status < 500) throw err;
+      if (attempt < RETRY_DELAYS_MS.length) {
+        await new Promise((r) => setTimeout(r, RETRY_DELAYS_MS[attempt]));
+      }
+    }
+  }
+  throw lastError;
 }
 
 module.exports = { fetchOrders };
diff --git a/src/format.js b/src/format.js
--- a/src/format.js
+++ b/src/format.js
@@ -4,3 +4,8 @@ function formatDate(d) {
   return d.toISOString().slice(0, 10);
 }
 
-module.exports = { formatDate };
+function formatMoney(cents, currency = 'USD') {
+  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100);
+}
+
+module.exports = { formatDate, formatMoney };
```
