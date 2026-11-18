# Check paid revenue before delivery

A paid order contributes 120 units. A cancelled order contributes zero. The two fixtures differ in how they handle that second order.

From the root of the repository, run:

```sh
python3 examples/order-review/replay.py
```

The replay launches two governed reviews with separate temporary memory directories. Both assessment scores describe the review dossier. The acceptance check executes each fixture and compares its result with the requirement. The CLI reports `delivery_accepted` only when a check was requested. Delivery requires both certification of the dossier and a successful check.

For your own trusted project, give the check as the last option:

```sh
python3 -m modex.engage --governed --project /path/to/project --acceptance-command python3 /absolute/path/to/check.py
```

The command runs locally with your permissions in the project directory, with a 60-second timeout. Use trusted code and fixtures. Exit zero signals success. Command output goes to stderr and the JSON receipt goes to stdout.
