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
    config: Option<PathBuf>,

    #[clap(short, long)]
    rpcuser: Option<String>,

    #[clap(short, long)]
    rpcpassword: Option<String>,

    #[clap(short, long, default_value_t = 8554)]
    rpcport: u16,

    #[clap(short, long, default_value_t = String::from("localhost"))]
    rpcbind: String,
}

fn main() {
    let args = Args::parse();

    let mut rpcuser = String::default();
    let mut rpcpassword = String::default();
    let mut rpcport = String::default();
    let mut rpcbind = String::default();

    if let Some(config_file_path) = args.config {
        let mut config = Ini::new();
        // You can easily load a file to get a clone of the map:
        config.load(config_file_path.as_path()).unwrap();
        rpcuser = config.get("default", "rpcuser").unwrap();
        rpcpassword = config.get("default", "rpcpassword").unwrap();
        rpcport = config.get("main", "rpcport").unwrap();
        rpcbind = config.get("main", "rpcbind").unwrap();
    }

    rpcuser = args.rpcuser.unwrap_or_default();
    rpcpassword =args.rpcpassword.unwrap_or_default();
    rpcport = args.rpcport.to_string();
    rpcbind = args.rpcbind;


    let rpc = Client::new(
        &format!("http://{rpcbind}:{rpcport}"),
        Auth::UserPass(rpcuser, rpcpassword),
    )
    .unwrap();

    
    let mut prev_height = 0;
    let mut attempts = 0;
    let end_height = 10000;
    while prev_height < end_height {
        std::thread::sleep(std::time::Duration::from_secs(1));
        let blockchain_info = rpc.get_blockchain_info().unwrap();
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
