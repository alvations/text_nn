import torch
import torch.nn as nn
import torch.autograd as autograd
import torch.nn.functional as F
import rationale_net.models.cnn as cnn
import rationale_net.utils.train as utils
import pdb

'''
    The generator selects a rationale z from a document x that should be sufficient
    for the encoder to make it's prediction.
    Several froms of Generator are supported. Namely CNN with arbitary number of layers, and @taolei's FastKNN
'''
class Tagger(nn.Module):

    def __init__(self, embeddings, args):
        super(Tagger, self).__init__()
        vocab_size, hidden_dim = embeddings.shape
        self.embedding_layer = nn.Embedding( vocab_size, hidden_dim)
        self.embedding_layer.weight.data = torch.from_numpy( embeddings )
        self.embedding_layer.weight.requires_grad = False
        self.args = args
        if args.model_form == 'cnn':
            self.cnn = cnn.CNN(args, max_pool_over_time = False)

        self.hidden = nn.Linear((len(args.filters)* args.filter_num), args.num_tags)
        self.dropout = nn.Dropout(args.dropout)

    
    def forward(self, x_indx, mask):
        '''Given input x_indx of dim (batch, length), return z (batch, length) such that z
        can act as element-wise mask on x'''
        if self.args.model_form == 'cnn':
            x = self.embedding_layer(x_indx.squeeze(1))
            if self.args.cuda:
                x = x.cuda()
            x = torch.transpose(x, 1, 2) # Switch X to (Batch, Embed, Length)
            activ = self.cnn(x)
        else:
            raise NotImplementedError("Model form {} not yet supported for generator!".format(args.model_form))

        #pdb.set_trace()
        hidden = self.hidden
        logit = hidden(torch.transpose(activ, 1, 2))
        return logit, hidden
