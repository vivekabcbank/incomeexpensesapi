import facebook


class Facebook:

    @staticmethod
    def validate(auth_token):
        try:
            # import  pdb
            # pdb.set_trace()
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=id,first_name,last_name,middle_name,name,name_format,picture,short_name')
            return profile
        except:
            return "The token is invalid or expired."
