import boto3
import click
import requests


class Route53Ddns:
    def __init__(self, zone_id: str, name: str, verbose: int = 0) -> None:
        self.zone_id = zone_id
        self.name = name
        self._verbose = verbose

    def _get_ip_address(self) -> str:
        url = "https://ifconfig.io/all.json"

        res = requests.get(url)

        data = res.json()

        if self._verbose:
            click.echo(data)

        return data["ip"]

    def _change_record(self, ip: str) -> None:
        client = boto3.client("route53")

        result = client.change_resource_record_sets(
            HostedZoneId=self.zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": self.name,
                            "Type": "A",
                            "TTL": 3600,
                            "ResourceRecords": [
                                {
                                    "Value": ip,
                                }
                            ],
                        },
                    }
                ]
            },
        )

        if self._verbose:
            click.echo(result)

    def update(self) -> None:
        return self._change_record(self._get_ip_address())


@click.command()
@click.option("-v", "--verbose", count=True)
@click.option("--zone-id", envvar="ZONE_ID", help="hosted zone id")
@click.option(
    "--resource-record-name",
    envvar="RESOURCE_RECORD_NAME",
    help="resource record name (e.g. www.example.com)",
)
def main(verbose: int, zone_id: str, resource_record_name: str):
    route53_ddns = Route53Ddns(
        zone_id=zone_id,
        name=resource_record_name,
        verbose=verbose,
    )

    route53_ddns.update()


if __name__ == "__main__":
    main()
