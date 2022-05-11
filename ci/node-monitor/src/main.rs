use bitcoincore_rpc::{Auth, Client, RpcApi};
use configparser::ini::Ini;
use std::path::PathBuf;

use clap::Parser;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[clap(short, long)]
    config: PathBuf,
}

fn main() {
    let args = Args::parse();

    let config_file_path: PathBuf = args.config;
    let mut config = Ini::new();

    // You can easily load a file to get a clone of the map:
    config.load(config_file_path.as_path()).unwrap();
    let rpcuser = config.get("default", "rpcuser").unwrap();
    let rpcpassword = config.get("default", "rpcpassword").unwrap();
    let rpcport = config.get("main", "rpcport").unwrap();
    let rpcbind = config.get("main", "rpcbind").unwrap();

    let rpc = Client::new(
        &format!("http://{rpcbind}:{rpcport}"),
        Auth::UserPass(rpcuser, rpcpassword),
    )
    .unwrap();
    
    let blockchain_info = rpc.get_blockchain_info().unwrap();
    let mut prev_height = 0;
    let mut attempts = 0;
    let end_height = 10000;
    while prev_height < end_height {
        std::thread::sleep(std::time::Duration::from_secs(1));
        let height = blockchain_info.blocks;

        if prev_height == height {
            attempts -= 1;
        } else if height > prev_height {
            attempts = 60
        }
        if attempts >= 60 {
            println!("Block Stuck on ${prev_height} for 60 secs");
            break;
        }
        prev_height = height;
        println!("Block Height ${prev_height}");
    }
}
