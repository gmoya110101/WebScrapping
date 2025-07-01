class Product():
    def __init__(self, description:str, old_price:float, current_price:float, link:str):
        self.description = description
        self.old_price = old_price
        self.current_price = current_price
        self.link = link
        
    def to_dict(self):
        return {
            "Description": self.description,
            "Old Price": self.old_price,
            "Current Price": self.current_price,
            "Link": self.link
        }