from app.presentation.ui_theme import PageShell,empty_state
class AgriculturePage(PageShell):
    def __init__(self):
        super().__init__("الري والتسميد","خطط الري والتسميد ومتابعة التنفيذ.")
        self.content.addWidget(empty_state("واجهة الوحدة جاهزة. سيتم توصيل إجراءات الري والتسميد بطبقة التطبيق دون كسر البيانات الحالية."))
