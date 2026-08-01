---- MODULE PaxosLeaseChecked ----
(***************************************************************************)
(* PaxosLease together with the timing assumption under which it is safe.  *)
(* Safe configurations point TLC at this module.  Configurations that       *)
(* intentionally violate the quarantine bound point at PaxosLease.tla       *)
(* directly, so that TLC exhibits the resulting lease-exclusivity           *)
(* violation instead of rejecting the configuration.                        *)
(*                                                                          *)
(* Under the prepare-time timer rule the quarantine bound tracks the        *)
(* proposer attempt duration, not the acceptor exclusion duration: both a   *)
(* forgotten promise and a forgotten accepted lease can only matter         *)
(* through an attempt whose Prepare preceded the crash, and that attempt    *)
(* is unusable ProposerDuration later.  Quarantine >= AcceptorDuration is   *)
(* NOT required: see PaxosLeaseQuarantineEqualsProposer.cfg, which passes   *)
(* with Quarantine = ProposerDuration < AcceptorDuration.                   *)
(***************************************************************************)
EXTENDS PaxosLease

ASSUME Quarantine >= ProposerDuration

====
