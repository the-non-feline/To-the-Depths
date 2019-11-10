from . import ttd_tools, catalog

async def default_special_args_check(self, report, author, *args): 
        return True

async def valid_mentions(self, report, author, arg_name, *mentions, custom_error=None): 
    decoded = self.decode_mentions(report, *mentions) 

    if None in decoded: 
        report.add(custom_error or f'{author.mention}, argument `{arg_name}` must be valid mention(s). ') 
    else: 
        return decoded

async def valid_items(self, report, author, arg_name, *items, custom_error=None): 
    item_results = ttd_tools.bulk_search(catalog.items, items, converter=tuple) 

    if None in item_results: 
        report.add(custom_error or f'{author.mention}, argument `{arg_name}` must be valid item(s). ') 
    else: 
        return item_results

async def valid_side(self, report, author, arg_name, side, custom_error=None): 
    if side.lower() not in ('heads', 'tails'): 
        report.add(custom_error or f'{author.mention}, argument `{arg_name}` can only be `heads` or `tails`. ') 
    else: 
        return side

async def valid_amount(self, report, author, arg_name, amount, custom_error=None): 
    if not amount.isnumeric() or int(amount) <= 0: 
        report.add(custom_error or f'{author.mention}, argument `{arg_name}` must be valid amount(s). ') 
    else: 
        return int(amount) 