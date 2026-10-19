from src.prgen.providers.openrouter import OpenRouterProvider
from src.prgen.prompts import build_messages
from src.prgen.schema import PRDescription

diff = """
diff --git a/src/calculator.py b/src/calculator.py
index 3a5f2c1..7b8e9d4 100644
--- a/src/calculator.py
+++ b/src/calculator.py
@@ -1,5 +1,6 @@
 def add(a, b):
-    return a + b
+    result = a + b
+    return result
 
 def subtract(a, b):
     return a - b
"""
messages = build_messages(diff)

p = OpenRouterProvider()
raw = p.generate(messages, PRDescription.model_json_schema(), temperature=0.2)
print(raw)

pr = PRDescription.model_validate_json(raw)
print("VALIDATED:", pr.title)