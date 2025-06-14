from mdm.models import SMTPSettings


CATEGORY_LABELS = {
    1: "CaseType",
    2: "FileType",
    3: "CaseFiles",
    4: "Correspondence",
    5: "FileExtension",
    6: "CaseStatus",
    7: "ClassificationType"
}


def get_active_smtp_settings():
    return SMTPSettings.objects.filter(isActive=True).first()