from app.presentation.ui_theme import PageShell,empty_state
class OperationsPage(PageShell):
    def __init__(self):
        super().__init__("العمليات الزراعية والصيانة","أوامر العمل، الصيانة وتكلفة التنفيذ.")
        self.content.addWidget(empty_state("واجهة التشغيل والصيانة الموحدة جاهزة للربط مع خدمات العمليات الحالية."))
