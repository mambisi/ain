use structopt::clap::arg_enum;

#[derive(Debug)]
pub struct ChainParams {
    pub rpc_port: u16,
    pub base_dir: &'static str,
}

arg_enum! {
    #[derive(Debug)]
    pub enum Chain {
        Main,
        Testnet,
        Devnet,
        Regtest,
    }
}

impl Chain {
    pub fn get_params(&self) -> ChainParams {
        match self {
            Chain::Main => ChainParams {
                rpc_port: 8554,
                base_dir: "",
            },
            Chain::Testnet => ChainParams {
                rpc_port: 18554,
                base_dir: "testnet3",
            },
            Chain::Devnet => ChainParams {
                rpc_port: 20554,
                base_dir: "devnet",
            },
            Chain::Regtest => ChainParams {
                rpc_port: 19554,
                base_dir: "regtest",
            },
        }
    }
}