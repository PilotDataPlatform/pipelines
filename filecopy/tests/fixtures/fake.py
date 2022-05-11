import faker
import pytest
from common import GEIDClient


class Faker(faker.Faker):
    def geid(self) -> str:
        """Generate global entity id."""

        return GEIDClient().get_GEID()


@pytest.fixture
def fake() -> Faker:
    yield Faker()
