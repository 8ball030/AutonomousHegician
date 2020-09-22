import { ContractFactory, Signer } from "ethers";
import { Provider } from "ethers/providers";
import { UnsignedTransaction } from "ethers/utils/transaction";
import { WhitelistedAggregatorProxy } from "./WhitelistedAggregatorProxy";
export declare class WhitelistedAggregatorProxyFactory extends ContractFactory {
    constructor(signer?: Signer);
    deploy(_aggregator: string): Promise<WhitelistedAggregatorProxy>;
    getDeployTransaction(_aggregator: string): UnsignedTransaction;
    attach(address: string): WhitelistedAggregatorProxy;
    connect(signer: Signer): WhitelistedAggregatorProxyFactory;
    static connect(address: string, signerOrProvider: Signer | Provider): WhitelistedAggregatorProxy;
}
//# sourceMappingURL=WhitelistedAggregatorProxyFactory.d.ts.map