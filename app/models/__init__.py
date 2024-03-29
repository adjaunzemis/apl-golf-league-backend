# Monkeypatch
#
# Forces SQLModel to use AutoString for Enum fields
# Matches behavior prior to v0.0.9
#
# Ref: https://github.com/tiangolo/sqlmodel/discussions/717
#
# TODO: Remove this, migrate to new enums?

from sqlmodel import main as _sqlmodel_main
_sqlmodel_main.sa_Enum = lambda _: _sqlmodel_main.AutoString
