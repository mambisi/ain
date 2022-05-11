use bitcoincore_rpc::{Auth, Client, RpcApi};

fn main() {
    let rpc = Client::new(
        "http://localhost:8332",
        Auth::UserPass("".to_string(), "".to_string()),
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
            break 
        }
        prev_height = height;
        println!("Block Height ${prev_height}");
    }
}
