import asyncio, click, yaml
from fb_scraper.core.tasks import scrape_group
from fb_scraper.db.init import init_db
from fb_scraper.core.fb_login import ensure_login

@click.group()
def cli():
    pass

@cli.command()
def bootstrap():
    """Initialise DB and perform interactive Facebook login."""
    init_db()
    asyncio.run(ensure_login())
    click.echo("Bootstrap complete.")

@cli.command()
@click.argument("group_id")
def scrape(group_id: str):
    """Queue a scrape task for GROUP_ID."""
    cfg = yaml.safe_load(open("scrape_config.yaml"))
    if group_id not in cfg["groups"]:
        raise click.BadParameter(f"{group_id} not configured")
    tid = scrape_group.delay(cfg["groups"][group_id], group_id)
    click.echo(f"Queued task {tid}")

@cli.command("scrape-all")
def scrape_all_cmd():
    cfg = yaml.safe_load(open("scrape_config.yaml"))
    for gid, url in cfg["groups"].items():
        tid = scrape_group.delay(url, gid)
        click.echo(f"{gid}: queued {tid}")

if __name__ == "__main__":
    cli()
