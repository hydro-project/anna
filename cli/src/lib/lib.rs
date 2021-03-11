#![warn(clippy::unwrap_used)]

//! This is the rust `anna` Library for working with the `anna` key-value store. It is linked into
//! the `anna` CLI binary but can also be used by others to create new binaries
//!
#[macro_use]
extern crate error_chain;

pub mod info;

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