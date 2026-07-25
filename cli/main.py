import typer

from cli.campaign_commands import export, run
from cli.doctor_command import doctor
from cli.project_commands import create, ingest, plan

app = typer.Typer(name="rivet", no_args_is_help=True)


@app.callback()
def main() -> None:
    """Verified multimodal ad creation on one AMD Radeon GPU."""


app.command()(doctor)
app.command()(create)
app.command()(ingest)
app.command()(plan)
app.command()(run)
app.command()(export)


if __name__ == "__main__":
    app()
