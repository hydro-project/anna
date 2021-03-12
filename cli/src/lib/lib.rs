#![warn(clippy::unwrap_used)]

//! This is the rust `anna` Library for working with the `anna` key-value store. It is linked into
//! the `anna` CLI binary but can also be used by others to create new binaries
//!
#[macro_use]
extern crate error_chain;

use nix::unistd::Pid;
use sysinfo::{ProcessExt, System, SystemExt};
use nix::sys::signal::{kill, Signal};

pub mod info;

// Pending them being defined elsewhere in a build script or similar
const ANNA_MONITOR_PROCESS_NAME: &str = "anna-monitor";
const ANNA_ROUTE_PROCESS_NAME: &str = "anna-route";
const ANNA_KVS_PROCESS_NAME: &str = "anna-kvs";
const KILL_LIST: [&str;3] = [ ANNA_MONITOR_PROCESS_NAME, ANNA_ROUTE_PROCESS_NAME, ANNA_KVS_PROCESS_NAME];

// We'll put our errors in an `errors` module, and other modules in this crate will
// `use crate::errors::*;` to get access to everything `error_chain!` creates.
#[doc(hidden)]
pub mod errors {
    // Create the Error, ErrorKind, ResultExt, and Result types
    error_chain! {}
}

#[doc(hidden)]
error_chain! {
    types {
        Error, ErrorKind, ResultExt, Result;
    }

    foreign_links {
        Io(std::io::Error);
    }
}

/*
    Gather a list of pids that are running for a process using the process name
 */
fn pids_from_name(name: &str) -> Vec<i32> {
    let s = System::new_all();
    s.get_process_by_name(name).iter().map(|p| p.pid()).collect()
}

/// `stop` function terminates the running processes for `anna-kvs`, `anna-monitor` and `anna-route`
///
/// It returns a Result<String> with a String describing the actions that were taken
pub fn stop() -> Result<usize> {
    let mut kill_count: usize = 0;
    for process_name in KILL_LIST.iter() {
        for pid in pids_from_name(process_name) {
            if kill(Pid::from_raw(pid), Some(Signal::SIGTERM)).is_ok() {
                kill_count += 1;
            }
        }
    }

    Ok(kill_count)
}

#[cfg(test)]
mod test {
    #[test]
    fn no_such_process_to_stop() {
        assert_eq!(super::stop().expect("Expected zero processes killed"), 0);
    }
}