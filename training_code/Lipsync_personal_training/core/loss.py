import torch.nn.functional as F
from lib.loss import Loss, LossInterface


class MyModelLoss(LossInterface):
    def __init__(self, CONFIG):
        super(MyModelLoss, self).__init__(CONFIG)

    def get_loss_G(self, run_dict, model, prev_model, valid=False):
        L_G = 0.0

        if self.CONFIG["LOSS"]["W_ADV"]:
            L_adv = (-run_dict["g_pred_fake"]).mean()
            L_G += self.CONFIG["LOSS"]["W_ADV"] * L_adv
            self.loss_dict["L_g_adv"] = round(L_adv.item(), 4)

        if self.CONFIG["LOSS"]["W_ID"]:
            L_id = Loss.get_id_loss(run_dict["source_id"], run_dict["result_id"])
            L_G += self.CONFIG["LOSS"]["W_ID"] * L_id
            self.loss_dict["L_id"] = round(L_id.item(), 4)

        if self.CONFIG["LOSS"]["W_VGG"]:
            L_vgg = Loss.get_vgg_loss(
                F.interpolate(run_dict["cycle_fake_img"], (256, 256), mode="bilinear"),
                F.interpolate(run_dict["source_color"], (256, 256), mode="bilinear"),
            )
            L_G += self.CONFIG["LOSS"]["W_VGG"] * L_vgg
            self.loss_dict["L_vgg"] = round(L_vgg.item(), 4)

        if self.CONFIG["LOSS"]["W_LPIPS"]:
            L_lpips = Loss.get_lpips_loss(run_dict["result_img"], run_dict["gt_img"])
            L_G += self.CONFIG["LOSS"]["W_LPIPS"] * L_lpips
            self.loss_dict["L_lpips"] = round(L_lpips.item(), 4)

        if self.CONFIG["LOSS"]["W_L1"]:
            L_L1 = Loss.get_L1_loss(run_dict["result_img"], run_dict["gt_img"])
            L_G += self.CONFIG["LOSS"]["W_L1"] * L_L1
            self.loss_dict["L_L1"] = round(L_L1.item(), 4)

        if self.CONFIG["LOSS"]["W_RECON"]:
            L_recon = Loss.get_L1_loss(run_dict["output"], run_dict["gt_img"])
            L_G += self.CONFIG["LOSS"]["W_RECON"] * L_recon
            self.loss_dict["L_recon"] = round(L_recon.item(), 4)

        if self.CONFIG["LOSS"]["W_CYCLE"]:
            L_cycle = Loss.get_L1_loss(
                run_dict["cycle_color_map"]
                * (1 - run_dict["source_mask"][:, 0].unsqueeze(1)),
                run_dict["source_color"]
                * (1 - run_dict["source_mask"][:, 0].unsqueeze(1)),
            )
            L_G += self.CONFIG["LOSS"]["W_CYCLE"] * L_cycle
            self.loss_dict["L_cycle"] = round(L_cycle.item(), 4)

        # feat loss for Projected D
        if self.CONFIG["LOSS"]["W_FEAT"]:
            L_feat = Loss.get_L1_loss(
                run_dict["g_feat_fake"]["3"], run_dict["g_feat_real"]["3"]
            )
            L_G += self.CONFIG["LOSS"]["W_FEAT"] * L_feat
            self.loss_dict["L_feat"] = round(L_feat.item(), 4)

        if self.CONFIG["LOSS"]["W_SYNC"]:
            L_sync = Loss.get_sync_loss(
                run_dict["img_embedding"], run_dict["mel_embedding"]
            )
            L_G += self.CONFIG["LOSS"]["W_SYNC"] * L_sync
            self.loss_dict["L_sync"] = round(L_sync.item(), 4)

        if self.CONFIG["LOSS"]["W_REG_SYNC"]:
            L_reg_sync = Loss.get_sync_loss(
                run_dict["reg_img_embedding"], run_dict["reg_mel_embedding"]
            )
            L_G += self.CONFIG["LOSS"]["W_REG_SYNC"] * L_reg_sync
            self.loss_dict["L_reg_sync"] = round(L_reg_sync.item(), 4)

        if self.CONFIG["LOSS"]["W_W_REG"]:
            L_w_reg = Loss.get_weight_reg_loss(model, prev_model)
            L_G += self.CONFIG["LOSS"]["W_W_REG"] * L_w_reg
            self.loss_dict["L_w_reg"] = round(L_w_reg.item(), 4)
        ## feat loss for Multilayer D
        # if self.CONFIG['LOSS']['W_feat']:
        #     L_feat = .0
        #     for i in range(len(dict["g_pred_fake"])):
        #         for j in range(len(dict["g_pred_fake"][i])):
        #             L_feat += Loss.get_L1_loss(dict["g_pred_fake"][i][j], dict["g_pred_real"][i][j])
        #     L_G += self.CONFIG['LOSS']['W_feat'] * (L_feat / float(len(dict["g_pred_fake"])))
        #     self.loss_dict["L_feat"] = round(L_feat.item(), 4)

        if valid:
            self.loss_dict["valid_L_G"] += round(L_G.item(), 4)
        else:
            self.loss_dict["L_G"] = round(L_G.item(), 4)
        return L_G

    def get_loss_D(self, run_dict, valid=False):
        L_D = 0.0
        L_real = (F.relu(1 - run_dict["d_pred_real"])).mean()
        L_fake = (F.relu(1 + run_dict["d_pred_fake"])).mean()
        L_D = L_real + L_fake

        if valid:
            self.loss_dict["valid_L_D"] += round(L_D.item(), 4)
        else:
            self.loss_dict["L_real"] = round(L_real.item(), 4)
            self.loss_dict["L_fake"] = round(L_fake.item(), 4)
            self.loss_dict["L_D"] = round(L_D.item(), 4)

        return L_D
