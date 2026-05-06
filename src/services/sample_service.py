from src.core.generator import generate_random_samples
from src.core.models import SampleSelection, SelectionParams
from src.core.validators import (
    parse_and_validate_manual_samples,
    validate_mode,
    validate_params,
)


class SampleService:
    def create_samples_from_random(self, params: SelectionParams) -> SampleSelection:
        validated_params = validate_params(params)
        samples = generate_random_samples(
            m=validated_params.m,
            n=validated_params.n,
        )
        return SampleSelection(mode="random", samples=samples)

    def create_samples_from_manual(
        self,
        params: SelectionParams,
        text: str,
    ) -> SampleSelection:
        validated_params = validate_params(params)
        samples = parse_and_validate_manual_samples(
            text=text,
            m=validated_params.m,
            n=validated_params.n,
        )
        return SampleSelection(mode="manual", samples=samples)

    def get_samples(
        self,
        params: SelectionParams,
        mode: str,
        manual_text: str = "",
    ) -> SampleSelection:
        validated_mode = validate_mode(mode)

        if validated_mode == "random":
            return self.create_samples_from_random(params)
        if validated_mode == "manual":
            return self.create_samples_from_manual(params, manual_text)

        raise ValueError(f"Unsupported sample mode: {mode}")
