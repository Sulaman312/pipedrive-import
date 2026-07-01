"""Application-owned automation integrations.

AUT-02 is implemented in Pipedrive itself and therefore has no runtime code
here. Future webhook-driven automations, beginning with AUT-03, belong in this
package and can expose HTTP adapters through a dedicated Flask blueprint.
"""
