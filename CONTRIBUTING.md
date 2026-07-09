# Contributing to PyCHEMA

Thanks for interest in improving PyCHEMA.

## Ground rules

1. **Thermo honesty** — do not market results as flight-ready engine designs.
2. **CEA fidelity** — prefer official `cea` APIs and documented species names.
3. **Validation** — new physics paths should include a test or a reference citation.
4. **No legacy dump** — do not commit the private `Chema/` MATLAB archive, large binaries, or personal files.

## Dev setup

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m pychema.cli validate
```

## Useful PR types

- Additional validation cases (RP-1311 examples, literature)
- Propellant pairs with correct CEA thermo names + approximate densities
- GUI/UX improvements
- Documentation and citations

## Code style

- Python 3.11+, stdlib + numpy/scipy/pandas
- Keep the CEA wrapper thin; put product logic in sweeps/optimize/ranking

## License

Contributions are under Apache-2.0 (same as this repository).
