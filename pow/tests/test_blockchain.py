from blockchain import (
    DIFFICULTY,
    GENESIS_PREV,
    Block,
    genesis,
    mine,
    new_block,
    validate_chain,
)


def test_genesis_is_the_same_on_every_node():
    a, b = genesis(), genesis()
    assert a.hash == b.hash
    assert a.previous_hash == GENESIS_PREV


def test_mine_meets_the_fixed_difficulty():
    g = genesis()
    b = mine(new_block([g], [{"sender": "ana", "to": "beto", "amount": 1}]))
    assert b.hash.startswith("0" * DIFFICULTY)
    assert b.hash == b.compute_hash()
    assert b.previous_hash == g.hash


def test_tampering_changes_the_hash():
    b = mine(new_block([genesis()], [{"amount": 1}]))
    b.transactions = [{"amount": 999}]
    assert b.compute_hash() != b.hash


def test_validate_chain_rejects_a_tampered_chain():
    g = genesis()
    b = mine(new_block([g], [{"amount": 1}]))
    assert validate_chain([g, b])[0]
    b.transactions = [{"amount": 999}]
    assert not validate_chain([g, b])[0]


def test_validate_chain_rejects_a_foreign_genesis():
    fake = mine(Block(0, GENESIS_PREV, [{"msg": "another network"}], timestamp=0.0))
    ok, reason = validate_chain([fake])
    assert not ok
    assert "genesis" in reason


def test_validate_chain_rejects_a_broken_link():
    g = genesis()
    b1 = mine(new_block([g], [{"amount": 1}]))
    b2 = mine(new_block([g, b1], [{"amount": 2}]))
    b2.previous_hash = "0" * 64
    b2 = mine(b2)  # valid PoW on its own, but it no longer points to b1
    ok, reason = validate_chain([g, b1, b2])
    assert not ok
    assert "previous_hash" in reason


def test_validate_chain_rejects_a_block_without_pow():
    g = genesis()
    b = new_block([g], [{"amount": 1}])
    while b.compute_hash().startswith("0" * DIFFICULTY):  # make sure PoW is NOT met
        b.nonce += 1
    b.hash = b.compute_hash()  # honest hash, but nobody did the work
    ok, reason = validate_chain([g, b])
    assert not ok
    assert "difficulty" in reason
