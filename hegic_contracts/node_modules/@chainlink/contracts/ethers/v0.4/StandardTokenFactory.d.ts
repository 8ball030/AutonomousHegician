import { ContractFactory, Signer } from "ethers";
import { Provider } from "ethers/providers";
import { UnsignedTransaction } from "ethers/utils/transaction";
import { StandardToken } from "./StandardToken";
export declare class StandardTokenFactory extends ContractFactory {
    constructor(signer?: Signer);
    deploy(): Promise<StandardToken>;
    getDeployTransaction(): UnsignedTransaction;
    attach(address: string): StandardToken;
    connect(signer: Signer): StandardTokenFactory;
    static connect(address: string, signerOrProvider: Signer | Provider): StandardToken;
}
//# sourceMappingURL=StandardTokenFactory.d.ts.map