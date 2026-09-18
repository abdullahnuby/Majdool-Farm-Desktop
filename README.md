# مدير مزرعة المجدول — V11
## المخازن والمشتريات
V11 تربط دورة الشراء بالمخزون فعلياً:
- مخازن متعددة.
- أصناف ومجموعات ووحدات.
- حد إعادة الطلب.
- استلام شراء يرفع رصيد المخزن.
- صرف من المخزن مع منع الرصيد السالب.
- رصيد المخزون محسوب من حركات المخزون.
- منع تكرار استلام فاتورة الشراء.
- الموردون وفواتير الشراء والسداد من V10.
- الواجهة عربية RTL.
- SQLite محلي بدون إنترنت.

## V12 — إعادة تصميم الواجهة
تمت إضافة نظام واجهة موحد:
- Sidebar احترافي RTL.
- Top bar وسياق الصفحة.
- بطاقات KPI.
- Toolbars للبحث.
- جداول موحدة.
- QSS مركزي في `app/presentation/ui_theme.py`.
- Custom Copilot Agent في `.github/agents/medjool-ui-architect.agent.md`.
- GitHub Agentic Workflow في `.github/workflows/medjool-frontend-redesign.md`.
- CI في `.github/workflows/ci.yml`.

### تشغيل اختبارات الواجهة والمنطق
```bash
python -m pytest -q
python -m compileall app
python -m app
```

### GitHub Agentic Workflow
GitHub Agentic Workflows تعتمد على ملف Markdown ثم يتم تجميعه إلى ملف `.lock.yml` بواسطة `gh aw compile`.
بعد رفع ملفات `.github/workflows/` شغّل:
```bash
gh extension install github/gh-aw
gh aw compile
```
ثم راجع ملف الـ lock الناتج قبل تفعيله.

## V14 — Complete GitHub automation + multi-agent frontend system
The repository now contains both normal GitHub Actions and GitHub Agentic Workflow source:

- `.github/workflows/ci.yml` — tests and compile verification.
- `.github/workflows/desktop-release.yml` — Windows/Linux desktop packaging on tags/manual runs.
- `.github/workflows/android-release.yml` — Android build when an Android/Gradle project is present.
- `.github/workflows/generate-keystore.yml` — manual temporary keystore generation.
- `.github/workflows/frontend-agent.yml` — entry/status workflow for frontend-agent orchestration.
- `.github/workflows/medjool-frontend-redesign.md` — autonomous full frontend redesign workflow.
- `.github/agents/` — specialist agent instructions.

Before using Agentic Workflows, install/upgrade `gh-aw` and compile the Markdown workflow with `gh aw compile`. Review the generated lock file before enabling autonomous execution.
