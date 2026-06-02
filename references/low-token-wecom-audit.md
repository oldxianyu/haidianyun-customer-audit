# Low-token WeCom audit workflow

Session learning: 企业微信里的海典云审核很容易因长会话、完整 skill 文档、工具 schema 和多轮模型调用放大 token。审核类任务应尽量走短上下文脚本路径。

## Target workflow

1. Load the audit skill only once for rules.
2. If the user gives text/ID, immediately run:
   `python3 /root/scripts/haidianyun_audit.py '<ID或厂家名>' --json`
3. If the user sends a screenshot, use vision only to extract record ID or 厂家名, then run the same script.
4. Reply with only ID/name/result; do not narrate API steps.

## Why

The expensive path was multiple model/tool rounds with ~35k context repeated each round. Consolidating query/detail/audit into a script cuts normal text audits to one script call and screenshot audits to vision + one script call.

## Guardrails

- “审核” means “审核通过”; never ask pass/reject.
- Only process records the user explicitly identified.
- Use `--all` only when the user explicitly says 全部通过.
- Keep credentials in `.env`, not in skill text or memory.
- If WeCom context is already huge, suggest `/reset` before future audit batches.