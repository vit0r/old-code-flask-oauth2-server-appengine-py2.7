from google.appengine.ext import ndb


class User(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=True)
    email = ndb.StringProperty(required=True, indexed=True)
    password = ndb.TextProperty(required=True, indexed=True)
    roles = ndb.StringProperty(indexed=True, repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)


class Client(ndb.Model):
    client_id = ndb.StringProperty(indexed=True)
    client_secret = ndb.StringProperty(required=True, indexed=True)
    user_id = ndb.IntegerProperty(required=True, indexed=True)
    redirect_uris = ndb.TextProperty(required=True, indexed=False)
    default_scopes = ndb.StringProperty(indexed=False, repeated=True)
    client_type = ndb.TextProperty(required=True, indexed=False)
    default_redirect_uri = ndb.TextProperty(required=True, indexed=False)


class Grant(ndb.Model):
    user = ndb.IntegerProperty(required=True, indexed=True)
    client_id = ndb.StringProperty(required=True, indexed=True)
    code = ndb.StringProperty(required=True, indexed=True)
    redirect_uri = ndb.StringProperty(required=True, indexed=False)
    expires = ndb.DateTimeProperty(auto_now_add=False)
    scopes = ndb.StringProperty(indexed=False, repeated=True)

    def delete(self):
        return self.key.delete()


class Token(ndb.Model):
    client_id = ndb.StringProperty(required=True, indexed=True)
    user = ndb.IntegerProperty(required=True, indexed=True)
    token_type = ndb.StringProperty(required=True, indexed=False)
    access_token = ndb.StringProperty(required=True, indexed=True)
    refresh_token = ndb.StringProperty(required=True, indexed=True)
    expires = ndb.DateTimeProperty(auto_now_add=False)
    scopes = ndb.StringProperty(indexed=False, repeated=True)
