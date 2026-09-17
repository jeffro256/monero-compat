#include "mc_api.h"

#include "file_io_utils.h"
#include "serialization/binary_utils.h"
#include "wallet/wallet2.h"

using tx_construction_data = tools::wallet2::tx_construction_data;
using multisig_sig = tools::wallet2::multisig_sig;
using pending_tx = tools::wallet2::pending_tx;

namespace
{
tools::wallet2::pending_tx get_control_ptx()
{
    tools::wallet2::pending_tx ptx;

    // chosen by fair dice rolls
    constexpr rct::key random_k = {{
        212, 254, 56, 28, 12, 132, 215, 21,
        141, 228, 142, 149, 58, 189, 218, 96,
        213, 35, 45, 110, 74, 233, 66, 16,
        11, 243, 152, 153, 47, 131, 215, 116
    }};

    ptx.tx.version = 2;
    ptx.tx.unlock_time = 2121;
    ptx.tx.vin = {
        cryptonote::txin_to_key{
            .amount = 1,
            .key_offsets = {68123, 5878, 275, 2471, 11, 1},
            .k_image = rct::rct2ki(random_k)
        },
        cryptonote::txin_to_key{
            .amount = 88,
            .key_offsets = {65123, 578, 245, 2971, 17, 8},
            .k_image = rct::rct2ki(rct::hash2rct(crypto::cn_fast_hash(&random_k, 32)))
        },
    };
    ptx.tx.vout = {
        cryptonote::tx_out{
            .amount = 0,
            .target = cryptonote::txout_to_key(rct::rct2pk(random_k))
        },
        cryptonote::tx_out{
            .amount = 0,
            .target = cryptonote::txout_to_tagged_key(rct::rct2pk(random_k), crypto::view_tag{66})
        }
    };
    const size_t n_inputs = ptx.tx.vin.size();
    const size_t n_outputs = ptx.tx.vout.size();
    ptx.tx.extra.resize(32);
    memcpy(ptx.tx.extra.data(), &random_k, ptx.tx.extra.size());
    ptx.tx.rct_signatures.type = rct::RCTTypeBulletproofPlus;
    ptx.tx.rct_signatures.txnFee = 20010911;
    ptx.tx.rct_signatures.outPk.resize(n_inputs);
    ptx.tx.rct_signatures.ecdhInfo.resize(n_inputs);
    ptx.tx.rct_signatures.p.pseudoOuts.resize(n_inputs);
    size_t n_lr = 0;
    while ((1 << n_lr) < n_inputs) ++n_lr;
    n_lr += 6;
    auto &bpp = ptx.tx.rct_signatures.p.bulletproofs_plus.emplace_back();
    bpp.L.resize(n_lr);
    bpp.R.resize(n_lr);
    ptx.tx.rct_signatures.p.CLSAGs.resize(n_inputs);
    for (size_t input_idx = 0; input_idx < n_inputs; ++input_idx)
    {
        const size_t ring_size = boost::get<cryptonote::txin_to_key>(ptx.tx.vin.at(input_idx)).key_offsets.size();
        ptx.tx.rct_signatures.p.CLSAGs.at(input_idx).s.resize(ring_size);
    }

    ptx.dust = 80085;
    ptx.fee = 20260915;
    ptx.dust_added_to_fee = false;
    ptx.change_dts = cryptonote::tx_destination_entry(7 * COIN, {}, false);
    ptx.selected_transfers = {8, 2, 0, 9999999};
    ptx.key_images = "deadbeef42069a";
    ptx.tx_key = {{4}};
    ptx.additional_tx_keys = {{{4}}, {{45}}};
    ptx.dests.resize(n_outputs);
    ptx.multisig_sigs.resize(n_inputs);
    ptx.multisig_tx_key_entropy = rct::rct2sk(random_k);

    auto &ctx = ptx.construction_data;
    ctx.sources.resize(n_inputs, cryptonote::tx_source_entry{.outputs = {{}}});
    ctx.change_dts = ptx.change_dts;
    ctx.splitted_dsts = ptx.dests;
    ctx.splitted_dsts.push_back(ctx.change_dts);
    ctx.selected_transfers = ptx.selected_transfers;
    ctx.extra.resize(16);
    memcpy(ctx.extra.data(), &random_k, 16);
    ctx.unlock_time = ptx.tx.unlock_time;
    ctx.use_rct = true;
    ctx.rct_config = rct::RCTConfig{.range_proof_type = rct::RangeProofPaddedBulletproof,
        .bp_version = 0};
    ctx.use_view_tags = true;
    ctx.dests = ptx.dests;
    ctx.subaddr_account = 5;
    ctx.subaddr_indices = {2, 0, 3};
    return ptx;
}
} //anonymous namespace

namespace rct
{
bool operator==(const RCTConfig &a, const RCTConfig &b)
{
    return a.range_proof_type == b.range_proof_type
        && a.bp_version       == b.bp_version;
}

bool operator==(const multisig_kLRki &a, const multisig_kLRki &b)
{
    return a.k  == b.k
        && a.L  == b.L
        && a.R  == b.R
        && a.ki == b.ki;
}
} //namespace rct

namespace cryptonote
{
bool operator==(const tx_source_entry &a, const tx_source_entry &b)
{
    return a.outputs                     == b.outputs
        && a.real_output                 == b.real_output
        && a.real_out_tx_key             == b.real_out_tx_key
        && a.real_out_additional_tx_keys == b.real_out_additional_tx_keys
        && a.real_output_in_tx_index     == b.real_output_in_tx_index
        && a.amount                      == b.amount
        && a.rct                         == b.rct
        && a.mask                        == b.mask
        && a.multisig_kLRki              == b.multisig_kLRki;
}
} //namespace cryptonote

bool operator==(const tx_construction_data &a, const tx_construction_data &b)
{
    return a.sources            == b.sources
        && a.change_dts         == b.change_dts
        && a.splitted_dsts      == b.splitted_dsts
        && a.selected_transfers == b.selected_transfers
        && a.extra              == b.extra
        && a.unlock_time        == b.unlock_time
        && a.use_rct            == b.use_rct
        && a.rct_config         == b.rct_config
        && a.use_view_tags      == b.use_view_tags
        && a.dests              == b.dests
        && a.subaddr_account    == b.subaddr_account
        && a.subaddr_indices    == b.subaddr_indices;
}

bool eq(const multisig_sig &a, const multisig_sig &b)
{
    std::string a_sigs_blob;
    if (!::serialization::dump_binary(const_cast<rct::rctSig&>(a.sigs), a_sigs_blob))
        return false;

    std::string b_sigs_blob;
    if (!::serialization::dump_binary(const_cast<rct::rctSig&>(b.sigs), b_sigs_blob))
        return false;

    return a_sigs_blob     == b_sigs_blob
        && a.ignore        == b.ignore
        && a.used_L        == b.used_L
        && a.signing_keys  == b.signing_keys
        && a.total_alpha_G == b.total_alpha_G
        && a.total_alpha_H == b.total_alpha_H
        && a.c_0           == b.c_0
        && a.s             == b.s;
}

template <typename value_type>
bool eq(const std::vector<value_type> &a, const std::vector<value_type> &b)
{
    if (a.size() != b.size())
        return false;
    for (size_t i = 0; i < a.size(); ++i)
        if (!eq(a[i], b[i]))
            return false;
    return true;
}

bool operator==(const pending_tx &a, const pending_tx &b)
{
    try
    {
        const crypto::hash a_txid = cryptonote::get_transaction_hash(a.tx);
        const crypto::hash b_txid = cryptonote::get_transaction_hash(b.tx);
        
        return a_txid                    == b_txid
            && a.dust                    == b.dust
            && a.fee                     == b.fee
            && a.dust_added_to_fee       == b.dust_added_to_fee
            && a.change_dts              == b.change_dts
            && a.selected_transfers      == b.selected_transfers
            && a.key_images              == b.key_images
            && a.tx_key                  == b.tx_key
            && a.additional_tx_keys      == b.additional_tx_keys
            && a.dests                   == b.dests
            && eq(a.multisig_sigs,          b.multisig_sigs) // C++ operator lookup rules are so cool...
            && a.multisig_tx_key_entropy == b.multisig_tx_key_entropy
            && a.construction_data       == b.construction_data;
    }
    catch (...)
    {
        return false;
    }
}

MC_API_EXPORT int mc_PendingTx_write(const char *fname)
{
    try
    {
        tools::wallet2::pending_tx ptx = get_control_ptx();
        std::string ptx_blob;
        if (!serialization::dump_binary(ptx, ptx_blob))
            return -1;
        if (!epee::file_io_utils::save_string_to_file(fname, ptx_blob))
            return -2;
    }
    catch (...)
    {
        return -3;
    }

    return 0;
}

MC_API_EXPORT int mc_PendingTx_read_and_compare(const char *fname)
{
    try
    {
        std::string ptx_blob;
        if (!epee::file_io_utils::load_file_to_string(fname, ptx_blob))
            return -1;
        tools::wallet2::pending_tx ptx;
        if (!serialization::parse_binary(ptx_blob, ptx))
            return 1;
        return ptx == get_control_ptx() ? 0 : 1;
    }
    catch (...)
    {
        return -2;
    }
}
