#
# An object simulating the frp market functions in the playground
#

from __future__ import annotations

import math
import random

from typing            import Callable, cast, overload, Union
from typing_extensions import Self, Any, TypeAlias, TypeGuard

from rich.table        import Table
from rich              import box as rich_box
from rich.panel        import Panel

from frplib.env        import environment
from frplib.exceptions import (ConditionMustBeCallable, ComplexExpectationWarning, ContractError,
                               ConstructionError, FrpError, KindError, MismatchedDomain,)
from frplib.frps       import FRP, FrpDemoSummary
from frplib.kinds      import Kind, kind
from frplib.numeric    import Numeric, as_real, show_tuples, show_values
from frplib.output     import in_panel
from frplib.protocols  import SupportsKindOf
from frplib.vec_tuples import VecTuple

def emit(*a, **kw) -> None:
    environment.console.print(*a, **kw)

def paneled(obj: str, title=None):
    if environment.ascii_only:
        if title:
            return f"{title}\n{obj}"
        return obj

    return in_panel(obj, title=title)


class Market:
    """Provides a code interface to frp market functionality.

    All methods are class methods, implementing the following
    market commands:

      + show -- show a Kind
      + demo -- summarize the values of a large batch of like-Kinded FRPs
      + buy -- summarize payoffs when purchasing a batch of like-Kinded FRPs
               at a range of selected prices
      + compare -- compare two Kinds via summaries of common samples

    See the documentation for the individual methods for details.

    """

    @classmethod
    def show(cls, kind_spec: FRP | Kind | SupportsKindOf | str) -> None:
        """Replicates the show command in the market.

        This is here for completeness as it is just what you get by
        printing a Kind. This respects the terminal, giving rich output
        when possible.

        """
        k = kind(kind_spec)  # ATTN: check FRP expr only case though kind() may
        emit(paneled(k.show_full()))

    @classmethod
    def demo(cls, count: int, spec: FRP | Kind | SupportsKindOf | str, show=True, summary=True):
        """Replicates the demo command in the market.

        This is very similar to the FRP.sample function, except this also prints
        a view of the Kind used for the demo (when show=True). Accepts a Kind,
        an FRP, a string Kind format, or any object with a `kind_of` method.

        Parameters:

        + count - the number of samples to use 
        + spec  - a Kind, FRP, or suitable specification accepted by `kind`; 
                  this defines what is sampled
        + show [= True] - if True, print a description of the Kind just as the
                          market command does. If False, only the summary table
                          is returned.
        + summary [= True] - if True, the table is a summary, as in the market demo
                             command; if False, the table shows each individual sample.

        Returns: a table of sample results, which by default is displayed. Note that
        the return value is equivalent to that produced by `FRP.sample`.
        
        """
        if show:
            if isinstance(spec, FRP) and spec._kind is None:
                emit(f'Activated {count} FRPs')        
            else:
                k = kind(spec)
                emit(f'Activated {count} FRPs with kind')
                emit(paneled(k.show_full()))
        return FRP.sample(count, spec, summary)

    @classmethod
    def buy(cls, count: int, prices: list[float], kind_spec: FRP | Kind | SupportsKindOf | str) -> None:
        """Replicates the buy command in the market.

        Prints a table of results as in the market.

        Parameters:

        + count - the number of samples to use 
        + prices - the list of prices (in dollars) at which purchases are made
        + kind_spec  - a Kind, FRP, or suitable specification accepted by `kind`; 
                  this defines what is sampled

        Returns: None.
        
        """
        if count <= 0:
            return
     
        k: Kind = kind(kind_spec)  # ATTN: expr only case needs to be handled (possibly with error)
        prices = sorted(prices)
     
        real_prices: list[Numeric] = []
        net_payoffs: list[VecTuple] = []
        net_per_unt: list[VecTuple] = []
        n = as_real(count)
        for price in prices:
            real_price: Numeric = as_real(price)
            total: VecTuple = sum(k.sample(count))
            net: VecTuple = total - n * real_price
            per_unit: VecTuple = net / n
     
            real_prices.append(real_price)
            net_payoffs.append(net)
            net_per_unt.append(per_unit)
            # fields = {
            #     'price': nroundx(real_price, mask=as_real('1.00')),
            #     'net': net,
            #     'net-per-unit': per_unit
            #     'ps':
            # }
            # widths = (0, 0, 0)
            # widths = tuple(map(max, zip(widths, (fields['price'], fields['net'], fields['net/u']))))
            # payoffs.append(fields)
     
        real_prices_s = show_values(real_prices, max_denom=1)
        net_payoffs_s = show_tuples(net_payoffs, max_denom=1)
        net_per_unt_s = show_tuples(net_per_unt, max_denom=1)
     
        emit(f'Buying {int(count):,} FRPs with kind')
        emit(paneled(k.show_full()))
        emit('at each price')
     
        if environment.ascii_only:
            out: list[str] = []
            for i in range(len(prices)):
                out.append("  {price:<12}  {net:>16}    {perunit:>12}".format(
                    price='$' + real_prices_s[i],
                    net='$' + net_payoffs_s[i],
                    perunit='$' + net_per_unt_s[i]
                ))
     
            header = "{price:<12}    {net:>16}    {perunit:>12}".format(
                price='Price/Unit',
                net='Net Payoff',
                perunit='Net Payoff/Unit'
            )
            emit(header + '\n' + "\n".join(out))
        else:
            # ATTN: Put styles in a more central place (environment?), e.g., environment.styles['values']
            table = Table(box=rich_box.SQUARE_DOUBLE_HEAD)
            table.add_column('Price/Unit ($)', justify='right', style='#4682b4', no_wrap=True)
            table.add_column('Net Payoff ($)', justify='right')
            table.add_column('Net Payoff/Unit ($)', justify='right', style='#6a6c6e')
     
            for i in range(len(prices)):
                table.add_row(
                    real_prices_s[i],
                    net_payoffs_s[i],
                    net_per_unt_s[i]
                )
            emit(table)
     
            return None

    @classmethod
    def compare(cls, count: int, kind_spec1: FRP | Kind | SupportsKindOf | str, kind_spec2: FRP | Kind | SupportsKindOf | str) -> None:
        """Replicates the buy command in the market.

        Prints a display of the two Kinds used and table of results as in the market.

        Parameters:

        + count - the number of samples to use 
        + kind_spec1  - a Kind, FRP, or suitable specification accepted by `kind`; 
                  this defines what is sampled for the first Kind
        + kind_spec2  - a Kind, FRP, or suitable specification accepted by `kind`; 
                  this defines what is sampled for the second Kind

        Returns: None.
        
        """
        k1 = kind(kind_spec1)  # ATTN: check FRP expr only case though kind() may 
        k2 = kind(kind_spec2)  # ATTN: check FRP expr only case though kind() may 

        emit(f'Comparing {count} activated FRPs each for two kinds, A and B.')
     
        emit(paneled(k1.show_full(), title='Kind A'))
        emit(paneled(k2.show_full(), title='Kind B'))
     
        for k, which in [(k1, 'A'), (k2, 'B')]:
            summary = FrpDemoSummary()
            for sample in k.sample(count):
                summary.add(sample)
            emit(summary.table(environment.ascii_only, title=f'Summary of Demo for Kind {which}'))
