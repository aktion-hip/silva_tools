##title=SiteRoot switcher
##parameters=model_id
model = getattr(container, model_id)

id = model.id
parent = model.aq_parent
model.to_publication()
model = getattr(parent, id)
context.REQUEST.set('model', model)
model.sec_update_last_author_info()
return "Changed %s into publication." %id
