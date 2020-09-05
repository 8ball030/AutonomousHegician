import { ContractFactory, Signer } from "ethers";
import { Provider } from "ethers/providers";
import { UnsignedTransaction } from "ethers/utils/transaction";
import { Arrayish, BigNumberish } from "ethers/utils";
import { WhitelistedAggregator } from "./WhitelistedAggregator";
export declare class WhitelistedAggregatorFactory extends ContractFactory {
    constructor(signer?: Signer);
    deploy(_link: string, _paymentAmount: BigNumberish, _timeout: BigNumberish, _decimals: BigNumberish, _description: Arrayish): Promise<WhitelistedAggregator>;
    getDeployTransaction(_link: string, _paymentAmount: BigNumberish, _timeout: BigNumberish, _decimals: BigNumberish, _description: Arrayish): UnsignedTransaction;
    attach(address: string): WhitelistedAggregator;
    connect(signer: Signer): WhitelistedAggregatorFactory;
    static connect(address: string, signerOrProvider: Signer | Provider): WhitelistedAggregator;
}
//# sourceMappingURL=WhitelistedAggregatorFactory.d.ts.map