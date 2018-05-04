********************
Namespace Protection
********************

A transaction family is defined by a set of parameters including a
name, some version numbers, an *apply* function and namespaces. The
apply function is what defines the behavior of a transaction family
according to the `get` and `set` operations on addresses of the Global
State. The goal of having a family declaring namespaces is to indicate
the subset of addresses it will use for its `get` (read, inputs) and
`set` (write, outputs) operations. It is important to remind that the
namespace is not a 1-to-1 relationship between namespaces and
transaction families.  Some transaction families like :doc:`Settings
Transaction Family
<../transaction_family_specifications/settings_transaction_family>` or
:doc:`BlockInfo Transaction Family
<../transaction_family_specifications/blockinfo_transaction_family>`
write data at addresses that other transaction families could use,
e.g. an onchain setting or the timestamp of the latest
block. Nevertheless, for security reasons, it is important to make
sure transaction families cannot tamper data at addresses they only
intend to read.  To this end, and when explicitly activated, the
validators can verify that transaction processors only perform `set`
operations whose addresses have a prefix in common with one of the
family’s specified namespace prefix(es). By default and for better
flexibility, this namespace protection is not enforced by the
validators, but when activated, this feature augments enforcement of
the transaction processors declaration done during registration.


In order to make validators enable namespace protection,
appropriate settings must be published on-chain using the
:doc:`Settings Transaction Family
<../transaction_family_specifications/settings_transaction_family>`.
For every block, a validator loads the JSON data stored under the
specific key ``sawtooth.validator.transaction_families``.  At this
key the data is a list of JSON entries, one per transaction family,
possibly including its namespaces.

Here is an example in which the namespaces are set for the transaction
families ``block_info``, ``sawtooth_settings`` and ``intkey``:

.. code-block:: python

  sawtooth.validator.transaction_families='[
    {\"family\": \"block_info\", \"version\": \"1.0\", \"namespaces\": [\"00b10c\"]},
    {\"family\":\"sawtooth_settings\", \"version\":\"1.0\"},
    {\"family\": \"intkey\", \"version\": \"1.0\", \"namespaces\": [\"1cf126\"]} ]'

In the case where a family has no ``"namespaces"``, the validator does
not restrict the write permission of the family. In the example above,
the family `sawtooth_settings` does not indicate any namespace and
therefore the validator will let it write at any address. This is
legitimate for :doc:`transaction
families<../transaction_family_specifications>` which are reviewed thoroughly,
like the ones included in Sawtooth.
