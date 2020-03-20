from decisionengine_modules.GCE.sources import GCEBillingInfo

# TODO
# The GCEBillingInfo module needs to be refactored so that tests
# can be written.  Then tests can be written to test smaller bits
# of code.  There is also an issue that the env has to have
# BOTO_CONFIG set, this has to be done outside of the code and
# can't be set in the test. Depending on how this testing is done
# you may be able to mock around this.

config_billing_info = {'projectId': 'hepcloud-fnal',
                       'lastKnownBillDate': '10/01/18 00:00',  # '%m/%d/%y %H:%M'
                       'balanceAtDate': 100.0,    # $
                       'accountName': 'None',
                       'accountNumber': 1111,
                       'credentialsProfileName': 'BillingBlah',
                       'applyDiscount': True,  # DLT discount does not apply to credits
                       'botoConfig': ".boto",
                       'localFileDir': "."}


class TestGCEBillingInfo:

    def test_produces(self):
        produces = ['GCE_Billing_Info']
        bi_pub = GCEBillingInfo.GCEBillingInfo(config_billing_info)
        assert bi_pub.produces() == produces

    def test_unable_to_download_filelist(self):
        calculator = GCEBillingInfo.GCEBillCalculator(projectId='hepcloud-fnal',
                                                      accountProfileName='BillingBlah',
                                                      accountNumber=1111,
                                                      lastKnownBillDate='10/01/18 00:00',
                                                      balanceAtDate=100.0,
                                                      applyDiscount=True,
                                                      botoConfig=".boto",
                                                      localFileDir=".")

        file_list = calculator._downloadBillFiles()
        assert file_list == []
