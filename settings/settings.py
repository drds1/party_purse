from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings/settings.toml"],
    environments=True,
    load_dotenv=True,
)
