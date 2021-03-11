#![warn(clippy::unwrap_used)]
//! `anna` is a command line tool for working with the `anna` key-value store
//!
//! Execute `anna` or `anna --help` or `anna -h` at the comment line for a
//! description of the command line options.

#[macro_use]
extern crate error_chain;

use std::env;
use std::process::exit;

use clap::{App, Arg, SubCommand, ArgMatches};
use log::{debug, warn};
use simplog::simplog::SimpleLogger;
use sysinfo::{ProcessExt, System, SystemExt};
use nix::sys::signal::{kill, Signal};
use annalib::info;
use nix::unistd::Pid;

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
        Clap(clap::Error);
    }
}

fn main() {
    match run() {
        Err(ref e) => {
            println!("error: {}", e);

            for e in e.iter().skip(1) {
                println!("caused by: {}", e);
            }

            // The backtrace is generated if env var `RUST_BACKTRACE` is set to `1` or `full`
            if let Some(backtrace) = e.backtrace() {
                println!("backtrace: {:?}", backtrace);
            }

            exit(1);
        }
        Ok(msg) => {
            if !msg.is_empty() {
                println!("{}", msg);
            }
            exit(0)
        }
    }
}

/*
    run the cli using clap to interpret commands and options
*/
fn run() -> Result<String> {
    let app = get_app();
    let app_clone= app.clone();
    let matches = app.get_matches();

    // Initialize the logger with the level of verbosity requested via option (or the default)
    SimpleLogger::init_prefix(matches.value_of("verbosity"), false);

    debug!("'{}' CLI version {}", env!("CARGO_PKG_NAME"), env!("CARGO_PKG_VERSION"));
    debug!("'anna' library version {}", info::version());

    match matches.subcommand() {
        ("help", arg_matches) => return help(app_clone, arg_matches),
        ("stop", arg_matches) => return stop(app_clone, arg_matches),
        (_, _) => Ok("No command executed".into())
    }
}

/*
    Gather a list of pids that are running for a process using the process name
 */
fn pids_from_name(name: &str) -> Vec<i32> {
    let s = System::new_all();
    let mut pids = vec!();
    for process in s.get_process_by_name(name) {
        pids.push(process.pid());
    }

    pids
}

/*
    The 'stop' command - will kill all the running ana related background processes locally
*/
fn stop(_app: App, _arg_matches: Option<&ArgMatches>) -> Result<String> {
    let mut pids: Vec<i32> = vec!();
    for process_name in KILL_LIST.iter() {
        let mut pids_of_process = pids_from_name(process_name);
        pids.append(&mut pids_of_process);
    }

    let mut kill_count = 0;
    for pid in pids {
        if kill(Pid::from_raw(pid), Some(Signal::SIGTERM)).is_ok() {
            kill_count += 1;
        }
    }

    Ok(format!("{} anna processes were terminated", kill_count))
}

/*
    The 'help' command
*/
fn help(mut app: App, _arg_matches: Option<&ArgMatches>) -> Result<String> {
    app.print_long_help()?;
    Ok("".into())
}

/*
    Create the clap app with the desired options and sub commands
*/
fn get_app() -> App<'static, 'static> {
    App::new(env!("CARGO_PKG_NAME"))
        .version(env!("CARGO_PKG_VERSION"))
        .arg(Arg::with_name("verbosity")
            .short("v")
            .long("verbosity")
            .takes_value(true)
            .value_name("VERBOSITY_LEVEL")
            .help("Set verbosity level for output (trace, debug, info, warn, error (default))"))
        .subcommand(SubCommand::with_name("stop")
            .about("Stop running instances of anna (monitor, route and kvs)"))
}