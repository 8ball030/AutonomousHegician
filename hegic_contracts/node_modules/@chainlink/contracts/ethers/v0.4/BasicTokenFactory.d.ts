import { ContractFactory, Signer } from "ethers";
import { Provider } from "ethers/providers";
import { UnsignedTransaction } from "ethers/utils/transaction";
import { BasicToken } from "./BasicToken";
export declare class BasicTokenFactory extends ContractFactory {
    constructor(signer?: Signer);
    deploy(): Promise<BasicToken>;
    getDeployTransaction(): UnsignedTransaction;
    attach(address: string): BasicToken;
    connect(signer: Signer): BasicTokenFactory;
    static connect(address: string, signerOrProvider: Signer | Provider): BasicToken;
}
//# sourceMappingURL=BasicTokenFactory.d.ts.map