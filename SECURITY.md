# Security

Please report vulnerabilities privately through GitHub's "Report a vulnerability" feature on this
repository (Security tab), not through public issues.

Notes for users: `objdict` has no dependencies and performs no I/O, `eval` or unpickling. Reading
a missing key from `Rdict`/`Objdict` creates it, and `update`/`deepcopy` recurse on nested input, so
do not use these types to hold or probe untrusted, attacker-sized data without limits.
