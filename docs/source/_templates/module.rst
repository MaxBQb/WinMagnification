{{ fullname | escape | underline}}

.. |upleft| replace:: :octicon:`arrow-up-left;1em;sd-text-success`
.. |downright| replace:: :octicon:`arrow-down-right;1em;sd-text-success`
.. |up| replace:: :octicon:`arrow-up;1em;sd-text-success`
.. |down| replace:: :octicon:`arrow-down;1em;sd-text-success`
.. |left| replace:: :octicon:`arrow-left;1em;sd-text-success`
.. |right| replace:: :octicon:`arrow-right;1em;sd-text-success`
.. |accessor getter| replace:: :octicon:`eye;1em;sd-text-warning` :bdg-warning:`Get`
.. |accessor setter| replace:: :octicon:`pencil;1em;sd-text-success` :bdg-success:`Set`
.. |accessor deleter| replace:: :octicon:`trash;1em;sd-text-danger` :bdg-danger:`Delete`
.. |accessors: get| replace:: **Accessors**: |accessor getter| :bdg-success-line:`Readonly`
.. |accessors: get set| replace:: **Accessors**: |accessor getter| |accessor setter|
.. |accessors: get set delete| replace:: **Accessors**: |accessor getter| |accessor setter| |accessor deleter|

.. automodule:: {{ fullname }}
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:
