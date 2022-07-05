{{ fullname | escape | underline}}

{% block modules %}
{% if modules %}
.. autosummary::
   :toctree:
   :template: module.rst
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

.. automodule:: {{ fullname }}
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:
