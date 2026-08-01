# Verification and Test Results

Generated: `2026-07-17T12:13:29.788647+00:00`

## tool-versions

Command: `bash -lc java -version 2>&1; tlapm --version; sany >/dev/null 2>&1; tlc -h 2>&1 | head -n 3; python --version; .venv/bin/python -m pytest --version; jar=$(grep -oE '[^ ]*tla2tools[^ ]*\.jar' "$(command -v tlc)" | head -n 1); [ -n "$jar" ] && sha256sum "$jar" || echo 'tla2tools.jar not located from tlc wrapper'`

Status: **PASS**

```text
openjdk version "17.0.19" 2026-04-21
OpenJDK Runtime Environment (build 17.0.19+10-1-deb12u2-Debian)
OpenJDK 64-Bit Server VM (build 17.0.19+10-1-deb12u2-Debian, mixed mode, sharing)
1.5.0

[1mNAME[0m

Python 3.11.2
pytest 9.1.1
sha256sum: '(tla2tools.jar': No such file or directory
tla2tools.jar not located from tlc wrapper

```

## parse

Command: `make parse`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd spec && sany PaxosLease.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
cd spec && sany PaxosLeaseChecked.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
cd spec && sany PaxosLeasePaxos.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeasePaxos.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeasePaxos
cd spec && sany PaxosLeaseImpl.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseImpl.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeaseImpl
cd counterexamples && sany LateTimer.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/counterexamples/LateTimer.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module LateTimer
cd counterexamples && sany LateTimerSym.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/counterexamples/LateTimerSym.tla
Parsing file /home/mtrencseni/paxoslease/counterexamples/LateTimer.tla
Parsing file /tmp/TLC.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module LateTimer
Semantic processing of module TLC
Semantic processing of module LateTimerSym
cd counterexamples && sany OwnerOnlyRelease.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/counterexamples/OwnerOnlyRelease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module OwnerOnlyRelease
cd counterexamples && sany ScalarQuorumCounting.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/counterexamples/ScalarQuorumCounting.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module ScalarQuorumCounting
cd counterexamples && sany StaleOwnerOpen.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/counterexamples/StaleOwnerOpen.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module StaleOwnerOpen
cd proof && sany PaxosLeaseProof.tla

****** SANY2 Version 2.1 created 24 February 2014

Parsing file /home/mtrencseni/paxoslease/proof/PaxosLeaseProof.tla
Parsing file /tmp/Naturals.tla
Semantic processing of module Naturals
Semantic processing of module PaxosLeaseProof
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## lint

Command: `make lint`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python -m ruff check
All checks passed!
.venv/bin/python -m mypy
Success: no issues found in 25 source files
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## check-standalone

Command: `make check-standalone`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseBase.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 21 and seed -7260828070853478665 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1212240] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:13:33)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:13:33.
Progress(17) at 2026-07-17 12:13:36: 214,544 states generated (214,544 s/min), 65,611 distinct states found (65,611 ds/min), 18,226 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 4.4E-8
  based on the actual fingerprints:  val = 8.5E-9
1992396 states generated, 573975 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 29.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 5 and the 95th percentile is 3).
Finished in 09s at (2026-07-17 12:13:42)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseRenewRelease.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 44 and seed 767893632742347466 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1214209] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:13:43)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:13:43.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 6.0E-12
22158 states generated, 7717 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 29.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 4 and the 95th percentile is 3).
Finished in 01s at (2026-07-17 12:13:44)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseCrashRestart.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 65 and seed 659083799170369193 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1214899] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:13:44)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:13:45.
Progress(13) at 2026-07-17 12:13:48: 397,421 states generated (397,421 s/min), 117,277 distinct states found (117,277 ds/min), 59,419 states left on queue.
Progress(24) at 2026-07-17 12:14:48: 38,426,435 states generated (38,029,014 s/min), 7,367,976 distinct states found (7,250,699 ds/min), 1,016,655 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 2.7E-5
  based on the actual fingerprints:  val = 9.0E-6
59115853 states generated, 10059404 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 36.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 01min 33s at (2026-07-17 12:15:17)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseDrift.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 124 and seed 1083666102290983090 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1232261] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:15:18)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:15:19.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 7.2E-11
87561 states generated, 19656 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 21.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 6 and the 95th percentile is 3).
Finished in 01s at (2026-07-17 12:15:20)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseQuarantineEqualsProposer.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 93 and seed 2857947655477862267 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1232944] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:15:20)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:15:20.
Progress(12) at 2026-07-17 12:15:23: 277,995 states generated (277,995 s/min), 86,532 distinct states found (86,532 ds/min), 47,231 states left on queue.
Progress(21) at 2026-07-17 12:16:23: 37,025,146 states generated (36,747,151 s/min), 7,674,543 distinct states found (7,588,011 ds/min), 1,865,722 states left on queue.
Progress(25) at 2026-07-17 12:17:23: 77,018,176 states generated (39,993,030 s/min), 14,223,713 distinct states found (6,549,170 ds/min), 1,693,525 states left on queue.
Progress(33) at 2026-07-17 12:18:23: 118,521,743 states generated (41,503,567 s/min), 20,106,854 distinct states found (5,883,141 ds/min), 290,026 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 1.1E-4
  based on the actual fingerprints:  val = 7.3E-5
121847029 states generated, 20447948 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 39.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 03min 09s at (2026-07-17 12:18:29)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseQuarantineEqualsProposer23.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 9 and seed 5727599782993452236 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1268902] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:18:30)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:18:31.
Progress(13) at 2026-07-17 12:18:34: 475,305 states generated (475,305 s/min), 138,068 distinct states found (138,068 ds/min), 68,441 states left on queue.
Progress(24) at 2026-07-17 12:19:34: 39,452,461 states generated (38,977,156 s/min), 7,472,145 distinct states found (7,334,077 ds/min), 927,454 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 2.6E-5
  based on the actual fingerprints:  val = 3.8E-6
57995085 states generated, 9867548 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 37.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 01min 29s at (2026-07-17 12:20:00)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseRedeliver.cfg PaxosLeaseChecked.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 79 and seed 3053509069371775477 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1286578] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseChecked.tla
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLease.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLease
Semantic processing of module PaxosLeaseChecked
Starting... (2026-07-17 12:20:01)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:20:01.
Progress(14) at 2026-07-17 12:20:04: 288,883 states generated (288,883 s/min), 66,070 distinct states found (66,070 ds/min), 30,075 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 1.0E-6
  based on the actual fingerprints:  val = 1.5E-7
12054516 states generated, 1857563 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 27.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 27s at (2026-07-17 12:20:28)
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## check-composition

Command: `make check-composition`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd spec && tlc -cleanup -workers 8 -difftrace PaxosLeasePaxos.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 97 and seed -1092254233500597624 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1291110] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeasePaxos.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeasePaxos
Starting... (2026-07-17 12:20:29)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:20:29.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 2.6E-13
4414 states generated, 2095 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 20.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 3 and the 95th percentile is 2).
Finished in 00s at (2026-07-17 12:20:30)
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## counterexamples

Command: `make counterexamples`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd counterexamples && (tlc -cleanup -workers 8 -difftrace -config LateTimer.cfg LateTimer.tla || true) > ../results/counterexample-latetimer.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/counterexample-latetimer.txt
cd counterexamples && (tlc -cleanup -workers 8 -difftrace -config OwnerOnlyRelease.cfg OwnerOnlyRelease.tla || true) > ../results/counterexample-owneronlyrelease.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/counterexample-owneronlyrelease.txt
cd counterexamples && (tlc -cleanup -workers 8 -difftrace -config ScalarQuorumCounting.cfg ScalarQuorumCounting.tla || true) > ../results/counterexample-scalarquorumcounting.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/counterexample-scalarquorumcounting.txt
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## check-impl

Command: `make check-impl`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplTimelyShipped.cfg PaxosLeaseImpl.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 61 and seed 7919949963629955670 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1302199] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseImpl.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeaseImpl
Starting... (2026-07-17 12:21:34)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:21:34.
Progress(12) at 2026-07-17 12:21:37: 470,601 states generated (470,601 s/min), 148,100 distinct states found (148,100 ds/min), 80,171 states left on queue.
Progress(21) at 2026-07-17 12:22:37: 38,300,673 states generated (37,830,072 s/min), 8,156,629 distinct states found (8,008,529 ds/min), 1,796,702 states left on queue.
Progress(25) at 2026-07-17 12:23:37: 79,797,968 states generated (41,497,295 s/min), 15,022,065 distinct states found (6,865,436 ds/min), 1,230,527 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 8.4E-5
  based on the actual fingerprints:  val = 3.7E-6
103018265 states generated, 18160464 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 37.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 02min 36s at (2026-07-17 12:24:10)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplTimelyBoundary.cfg PaxosLeaseImpl.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 48 and seed -434946735417721652 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1333330] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseImpl.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeaseImpl
Starting... (2026-07-17 12:24:11)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:24:11.
Progress(13) at 2026-07-17 12:24:14: 546,639 states generated (546,639 s/min), 170,179 distinct states found (170,179 ds/min), 91,307 states left on queue.
Progress(20) at 2026-07-17 12:25:14: 36,857,692 states generated (36,311,053 s/min), 8,505,283 distinct states found (8,335,104 ds/min), 2,563,538 states left on queue.
Progress(22) at 2026-07-17 12:26:14: 75,139,176 states generated (38,281,484 s/min), 16,193,909 distinct states found (7,688,626 ds/min), 3,708,746 states left on queue.
Progress(24) at 2026-07-17 12:27:14: 115,409,979 states generated (40,270,803 s/min), 23,217,518 distinct states found (7,023,609 ds/min), 3,675,599 states left on queue.
Progress(26) at 2026-07-17 12:28:14: 157,414,500 states generated (42,004,521 s/min), 29,746,689 distinct states found (6,529,171 ds/min), 2,706,113 states left on queue.
Progress(30) at 2026-07-17 12:29:14: 200,063,105 states generated (42,648,605 s/min), 35,909,111 distinct states found (6,162,422 ds/min), 953,602 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 3.5E-4
  based on the actual fingerprints:  val = 1.9E-5
211453825 states generated, 37160904 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 37.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 05min 20s at (2026-07-17 12:29:31)
cd spec && tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplTimelyRDominantSafe.cfg PaxosLeaseImpl.tla
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Running breadth-first search Model-Checking with fp 74 and seed 8172326648896189449 with 8 workers on 8 cores with 14267MB heap and 64MB offheap memory [pid: 1391726] (Linux 6.1.0-49-amd64 amd64, Debian 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/mtrencseni/paxoslease/spec/PaxosLeaseImpl.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module PaxosLeaseImpl
Starting... (2026-07-17 12:29:32)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-07-17 12:29:33.
Progress(12) at 2026-07-17 12:29:36: 455,097 states generated (455,097 s/min), 144,121 distinct states found (144,121 ds/min), 78,639 states left on queue.
Progress(20) at 2026-07-17 12:30:36: 35,307,636 states generated (34,852,539 s/min), 8,196,828 distinct states found (8,052,707 ds/min), 2,518,536 states left on queue.
Progress(22) at 2026-07-17 12:31:36: 72,238,532 states generated (36,930,896 s/min), 15,664,752 distinct states found (7,467,924 ds/min), 3,714,592 states left on queue.
Progress(24) at 2026-07-17 12:32:36: 110,898,233 states generated (38,659,701 s/min), 22,536,803 distinct states found (6,872,051 ds/min), 3,805,131 states left on queue.
Progress(26) at 2026-07-17 12:33:36: 151,050,178 states generated (40,151,945 s/min), 28,872,888 distinct states found (6,336,085 ds/min), 2,974,115 states left on queue.
Progress(29) at 2026-07-17 12:34:36: 192,361,774 states generated (41,311,596 s/min), 34,909,556 distinct states found (6,036,668 ds/min), 1,437,231 states left on queue.
Model checking completed. No error has been found.
  Estimates of the probability that TLC did not check all reachable states
  because two distinct states had the same fingerprint:
  calculated (optimistic):  val = 3.6E-4
  based on the actual fingerprints:  val = 3.5E-5
213185929 states generated, 37476080 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 37.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 9 and the 95th percentile is 3).
Finished in 05min 35s at (2026-07-17 12:35:07)
cd spec && (tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplTimelyBelow.cfg PaxosLeaseImpl.tla || true) > ../results/impl-timely-below.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/impl-timely-below.txt
cd spec && (tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplTimelyRDominant.cfg PaxosLeaseImpl.tla || true) > ../results/impl-timely-rdominant.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/impl-timely-rdominant.txt
cd spec && (tlc -cleanup -workers 8 -difftrace -config PaxosLeaseImplDelayedShipped.cfg PaxosLeaseImpl.tla || true) > ../results/impl-delayed-shipped.txt 2>&1 && grep -q "Invariant LeaseExclusivity is violated" ../results/impl-delayed-shipped.txt
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## unsafe-configs

Command: `make unsafe-configs`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/check_unsafe_config.py
PaxosLeaseUnsafeQuarantine.cfg: TLC exhibits a lease-exclusivity violation (26-state trace)
PaxosLeaseUnsafeQuarantine12.cfg: TLC exhibits a lease-exclusivity violation (25-state trace)
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## prove

Command: `make prove`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
cd proof && tlapm --threads 8 PaxosLeaseProof.tla
(* loading fingerprints in ".tlacache/PaxosLeaseProof.tlaps/fingerprints" *)
(* created new ".tlacache/PaxosLeaseProof.tlaps/PaxosLeaseProof.thy" *)
(* fingerprints written in ".tlacache/PaxosLeaseProof.tlaps/fingerprints" *)
File "./PaxosLeaseProof.tla", line 1, character 1 to line 115, character 4:
[INFO]: All 15 obligations proved.
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## test

Command: `make test`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python -m pytest -q
...............................                                          [100%]
31 passed in 8.47s
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## monte-carlo

Command: `make monte-carlo`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/run_monte_carlo.py --schedules 10000 --steps 100
random schedules: 10000
steps per schedule: 100
total scheduler picks: 1000000
effective steps (state-changing): 469291
no-op picks (disabled operation chosen): 530709
seed: 20260713
max queued messages: 22
delivered messages: 137070
dropped messages: 34509
duplicated messages: 34424
time advances: 76695
acceptor crashes: 45995
  ... while a lease was active: 3659
acceptor restarts with messages in flight: 12502
proposer crashes: 43785
successful activations observed: 5083
result: all checked schedules preserved invariants
no-quarantine counterexample: lease exclusivity violated: {'p1', 'p2'}
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## expected-counterexamples

Command: `make expected-counterexamples`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/run_counterexamples.py
insufficient-quarantine [simulator-execution]: lease exclusivity violated: {'p2', 'p1'}
owner-only-release [illustrative-example]: owner-only release erased newer lease
duplicate-quorum-counting [unit-rule]: duplicate responses counted as a quorum
ballot-reuse-after-restart [unit-rule]: ballot reused after restart
skipped-paxos-recovery [composed-model-execution]: skipped recovery ignored a prior accepted value
unfenced-external-effect [illustrative-example]: unfenced resource accepted delayed stale owner operation
nonintersecting-reconfiguration [illustrative-example]: old and new lease quorums do not intersect
unsafe-clock-source [unit-rule]: wall-clock step made an expired lease look live
renewal-without-quorum [unit-rule]: failed renewal extended authority without a quorum
stale-accept-overwrites-newer [unit-rule]: stale lower-ballot accept overwrote newer promise
late-promise-reuse [simulator-execution]: lease exclusivity violated: {'p2', 'p1'}
stale-owner-open [simulator-execution]: lease exclusivity violated: {'p2', 'p1'}
split-brain-read-without-fence [unit-rule]: unfenced read was concurrent with a newer owner write
suspended-event-loop [simulator-execution]: lease exclusivity violated during event-loop suspension: node 0 master until 14330, node 2 master until 8000
unsigned-expiry-underflow [unit-rule]: unsigned expiry subtraction underflowed to 18446744073709551615 and passed the activation margin after the expiry guard had already been cleared
wrote /home/mtrencseni/paxoslease/results/counterexamples.json
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## variant-check

Command: `make variant-check`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/generate_variants.py --check
LateTimer.tla: matches base + declared weakening
OwnerOnlyRelease.tla: matches base + declared weakening
ScalarQuorumCounting.tla: matches base + declared weakening
StaleOwnerOpen.tla: matches base + declared weakening
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## trace-smoke-test

Command: `make trace-smoke-test`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/trace_smoke_test.py
trace smoke test passed (event schema + invariants on one happy-path acquisition; not TLA+ trace validation)
events: DeliverAccept, DeliverAccepted, DeliverPrepare, DeliverPromise, StartAcquire
steps: 13
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## timing-examples

Command: `make timing-examples`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/timing_examples.py
[
  {
    "acceptor_duration": 4,
    "acceptor_real_lower_bound": 4.0,
    "operation_margin": 0,
    "proposer_duration": 4,
    "proposer_real_upper_bound": 4.0,
    "quarantine_duration": 4,
    "quarantine_real_lower_bound": 4.0,
    "r_max": 1.0,
    "r_min": 1.0
  },
  {
    "acceptor_duration": 1031,
    "acceptor_real_lower_bound": 1020.7920792079208,
    "operation_margin": 10,
    "proposer_duration": 1000,
    "proposer_real_upper_bound": 1020.2020202020202,
    "quarantine_duration": 1031,
    "quarantine_real_lower_bound": 1020.7920792079208,
    "r_max": 1.01,
    "r_min": 0.99
  }
]
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```

## paper-claims

Command: `make paper-claims`

Status: **PASS**

```text
make[1]: Entering directory '/home/mtrencseni/paxoslease'
.venv/bin/python scripts/check_paper_claims.py
paper claims consistent: 14 traces, 11 recorded searches, 11 exhaustive counts, 30 snippets
make[1]: Leaving directory '/home/mtrencseni/paxoslease'

```
