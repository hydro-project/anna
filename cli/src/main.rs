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
use annalib::info;
use annalib;

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
        Anna(annalib::errors::Error);
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
        ("stop", _) => Ok(format!("{} anna processes were terminated", annalib::stop()
            .map_err(|e| e.to_string())?)),
        (_, _) => Ok("No command executed".into())
    }
}

// Tests of the cli

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